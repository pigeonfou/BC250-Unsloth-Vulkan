#!/usr/bin/env python3
"""Guarded, reversible patches for Unsloth Studio on SkillFishOS BC-250.
Only patches exact code structures confirmed on 2026-10-11; never guesses on updates.
"""
import argparse
import ast
import datetime
import os
from pathlib import Path
import shutil
import sys
import tempfile

MARK_GPU = 'BC250_VULKAN_PATCH_V1'
MARK_MEM = 'BC250_MEMORY_PATCH_V1'
ACCEL_OLD = ('        from core.inference.diffusion_engine_router import image_install_accelerator\n'
             '        return preferred_accelerator(')
ACCEL_NEW = ('        if __import__("os").environ.get("UNSLOTH_BC250_VULKAN") == "1":  # ' + MARK_GPU + '\n'
             '            return "vulkan"\n' + ACCEL_OLD)
DEVICE_OLD = ('            device = (\n'
              '                off_torch.accelerator\n'
              '                if off_torch is not None\n'
              '                else resolve_diffusion_device_target().device\n'
              '            )')
DEVICE_NEW = DEVICE_OLD + ('\n            if __import__("os").environ.get("UNSLOTH_BC250_VULKAN") == "1":  # ' + MARK_GPU + '\n'
                             '                device = "vulkan"')
MEM_OLD = '                extra_args = list(extra_args or []),'
MEM_NEW = ('                extra_args = (\n'
           '                    list(extra_args or [])\n'
           '                    + (["--auto-fit", "on", "--max-vram", "6"]\n'
           '                       if __import__("os").environ.get("UNSLOTH_BC250_VULKAN") == "1" else [])\n'
           '                ),  # ' + MARK_MEM)

def patch_content(path, src):
    if path.name == 'sd_cpp_backend.py':
        if MARK_GPU not in src and src.count("if __import__('os').environ.get('UNSLOTH_BC250_VULKAN') == '1':") == 2:
            return src, False  # previously installed manual patch
        n = src.count(MARK_GPU)
        if n == 2:
            return src, False
        if n:
            raise RuntimeError('Partial GPU patch detected; manual intervention required')
        if src.count(ACCEL_OLD) != 1 or src.count(DEVICE_OLD) != 1:
            raise RuntimeError('GPU version changed: expected locations absent or duplicated')
        return src.replace(ACCEL_OLD, ACCEL_NEW, 1).replace(DEVICE_OLD, DEVICE_NEW, 1), True
    if path.name == 'sd_cpp_server.py':
        if MARK_MEM not in src and 'BC250_MEMORY_PATCH' in src:
            return src, False  # previously installed manual patch
        if MARK_MEM in src:
            if src.count(MARK_MEM) != 1:
                raise RuntimeError('Memory patch duplicated')
            return src, False
        if src.count(MEM_OLD) != 1:
            raise RuntimeError('Server version changed: expected location absent or duplicated')
        return src.replace(MEM_OLD, MEM_NEW, 1), True
    raise ValueError(path)

def atomic_write(path, data, stat):
    fd, temp = tempfile.mkstemp(prefix='.bc250-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, stat.st_mode & 0o777)
        os.chown(temp, stat.st_uid, stat.st_gid)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def apply(directory):
    paths = [directory / 'sd_cpp_backend.py', directory / 'sd_cpp_server.py']
    prepared = []
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f'Missing file: {path}')
        src = path.read_text()
        target, changed = patch_content(path, src)
        ast.parse(target, filename=str(path))
        prepared.append((path, src, target, changed))
    pending = [p for p in prepared if p[3]]
    if not pending:
        print('OK: patches already present')
        return 0
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backups = []
    try:
        for path, src, target, _ in pending:
            bak = path.with_name(path.name + f'.before-bc250-{stamp}')
            shutil.copy2(path, bak)
            backups.append((path, bak))
            atomic_write(path, target, path.stat())
    except Exception:
        for path, bak in backups:
            shutil.copy2(bak, path)
        raise
    print('UPDATED:', ', '.join(p.name for p, _, _, _ in pending))
    for path, bak in backups:
        print('BACKUP:', bak)
    return 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        for name in ('sd_cpp_backend.py', 'sd_cpp_server.py'):
            path = args.directory / name
            if not path.exists():
                raise RuntimeError(f'Missing {path}')
            target, modified = patch_content(path, path.read_text())
            ast.parse(target)
            print(name, 'needs patch' if modified else 'patched')
        return 0
    return apply(args.directory)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, SyntaxError, RuntimeError) as exc:
        print(f'BC250 PATCH REFUSED: {exc}', file=sys.stderr)
        sys.exit(1)
