from solders.keypair import Keypair
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import base58
import time
import argparse

found_keypair = None
found_event = threading.Event()
attempts_count = 0
lock = threading.Lock()


def generate_keypair_with_conditions(prefix=None, suffix=None):
    global found_keypair, found_event, attempts_count

    local_count = 0
    while not found_event.is_set():
        keypair = Keypair()
        public_key = str(keypair.pubkey())
        local_count += 1

        if local_count >= 100:
            with lock:
                attempts_count += local_count
            local_count = 0

        match = True
        if prefix and not public_key.startswith(prefix):
            match = False
        if suffix and not public_key.endswith(suffix):
            match = False

        if match:
            with lock:
                attempts_count += local_count
            found_keypair = keypair
            found_event.set()
            break

    if local_count > 0:
        with lock:
            attempts_count += local_count


def print_status(prefix, suffix):
    start_time = time.time()
    last_count = 0

    prefix_len = len(prefix) if prefix else 0
    suffix_len = len(suffix) if suffix else 0
    total_length = prefix_len + suffix_len
    probability = (1 / 58) ** total_length if total_length > 0 else 1.0

    while not found_event.is_set():
        time.sleep(1)
        with lock:
            current_attempts = attempts_count
        elapsed = time.time() - start_time

        attempts_diff = current_attempts - last_count
        speed = attempts_diff / 1
        avg_speed = current_attempts / elapsed if elapsed > 0 else 0
        last_count = current_attempts

        eta_str = "预计剩余时间: 计算中..."
        if probability > 0 and avg_speed > 0:
            expected_total = 1 / probability
            remaining_attempts = expected_total - current_attempts
            if remaining_attempts > 0:
                expected_remaining = remaining_attempts / avg_speed
                if expected_remaining < 60:
                    eta_str = f"预计剩余时间: {expected_remaining:.2f}秒"
                elif expected_remaining < 3600:
                    eta_str = f"预计剩余时间: {expected_remaining / 60:.2f}分钟"
                elif expected_remaining < 86400:
                    eta_str = f"预计剩余时间: {expected_remaining / 3600:.2f}小时"
                else:
                    eta_str = f"预计剩余时间: {expected_remaining / 86400:.2f}天"
            else:
                eta_str = "预计剩余时间: 即将完成"

        status_line = (
            f"当前进度: {current_attempts:,} 次尝试 | "
            f"实时速度: {speed:,.0f}次/秒 | "
            f"平均速度: {avg_speed:,.0f}次/秒 | "
            f"已运行: {elapsed:.0f}秒 | {eta_str}"
        )
        print(f"\r{status_line.ljust(150)}", end="", flush=True)
    print()


def find_keypair_with_conditions(prefix=None, suffix=None, num_threads=16):
    global found_keypair, found_event, attempts_count

    found_keypair = None
    found_event.clear()
    attempts_count = 0

    status_thread = threading.Thread(target=print_status, args=(prefix, suffix))
    status_thread.daemon = True
    status_thread.start()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(generate_keypair_with_conditions, prefix, suffix)
                   for _ in range(num_threads)]

        for future in as_completed(futures):
            if found_event.is_set():
                for f in futures:
                    f.cancel()
                break

    if found_keypair:
        print("\n" + "=" * 50)
        print(f"Found matching keypair after {attempts_count:,} attempts!")
        print(f"Public Key: {found_keypair.pubkey()}")
        private_key = base58.b58encode(bytes(found_keypair)).decode()
        print(f"Private Key: {private_key}")
        print("=" * 50)
        return found_keypair
    else:
        print("\nSearch interrupted or conditions too strict.")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成符合特定条件的Solana密钥对")
    parser.add_argument("-prefix", type=str, help="公钥前缀（Base58格式）", default=None)
    parser.add_argument("-suffix", type=str, help="公钥后缀（Base58格式）", default=None)
    parser.add_argument("-num_threads", type=int,
                        help="使用的线程数（默认：16）",
                        default=16)

    args = parser.parse_args()

    find_keypair_with_conditions(
        prefix=args.prefix,
        suffix=args.suffix,
        num_threads=args.num_threads
    )