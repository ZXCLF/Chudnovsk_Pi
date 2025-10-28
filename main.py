import math
import multiprocessing as mp
from functools import reduce
import time
import sys
import os
import psutil

# 整数字符串转换的限制
sys.set_int_max_str_digits(10000000)


def check_memory_usage(threshold_gb=1.0):
    """检查内存使用情况，如果可用内存低于阈值则发出警告"""
    memory_info = psutil.virtual_memory()
    available_gb = memory_info.available / (1024 ** 3)
    if available_gb < threshold_gb:
        print(f"警告: 可用内存不足 {available_gb:.2f} GB，建议关闭其他程序")
        return False
    return True

def compute_pi_terms(start, end):
    """计算Chudkovsky级数的指定范围内的项（使用增量计算避免大阶乘）"""
    C = 640320**3
    
    # 初始化第一项（如果start>0，需要计算起始项的各个部分）
    if start == 0:
        # k=0时的各项值
        fact_6k = 1  # (6k)!
        fact_3k = 1  # (3k)!
        fact_k_cubed = 1  # (k!)^3
        C_power = 1  # C^k
        linear_term = 13591409  # 545140134*k + 13591409
    else:
        # 计算start项的初始值（这里简化处理）
        fact_6k = math.factorial(6 * start)
        fact_3k = math.factorial(3 * start)
        fact_k = math.factorial(start)
        fact_k_cubed = fact_k ** 3
        C_power = C ** start
        linear_term = 545140134 * start + 13591409
    
    total_num = 0
    total_den = 1
    
    for k in range(start, end + 1):
        if k > start:
            # 增量更新各个项，避免重复计算大阶乘
            # 更新 (6k)! = (6k-6)! * (6k-5)*(6k-4)*...*(6k)
            for i in range(6*k-5, 6*k+1):
                fact_6k *= i
            
            # 更新 (3k)! = (3k-3)! * (3k-2)*(3k-1)*(3k)
            for i in range(3*k-2, 3*k+1):
                fact_3k *= i
            
            # 更新 (k!)^3 = ((k-1)!)^3 * k^3
            fact_k_cubed *= k**3
            
            # 更新 C^k
            C_power *= C
            
            # 更新线性项
            linear_term += 545140134
        
        # 计算当前项的分子和分母
        sign = 1 if k % 2 == 0 else -1
        numerator = sign * fact_6k * linear_term
        denominator = fact_3k * fact_k_cubed * C_power
        
        # 累加到总和（使用分数运算）
        if numerator != 0:
            # 通分: a/b + c/d = (a*d + b*c) / (b*d)
            new_num = total_num * denominator + numerator * total_den
            new_den = total_den * denominator
            
            # 约分（使用gcd）
            gcd_val = math.gcd(abs(new_num), new_den)
            if gcd_val > 1:
                total_num = new_num // gcd_val
                total_den = new_den // gcd_val
            else:
                total_num, total_den = new_num, new_den
    
    return total_num, total_den

def high_precision_sqrt(n, precision):
    """使用牛顿迭代法计算整数n的平方根到指定精度"""
    # 初始猜测值
    x = n // 2
    if x == 0:
        x = 1
    
    # 牛顿迭代
    while True:
        y = (x + n // x) // 2
        if y >= x:
            break
        x = y
    
    # 对于高精度，我们需要缩放n
    scaled_n = n * 10**(2 * precision)
    x = scaled_n // 2
    if x == 0:
        x = 1
    
    prev_x = -1
    while x != prev_x:
        prev_x = x
        x = (x + scaled_n // x) // 2
    
    return x

def high_precision_division(numerator, denominator, digits):
    """高精度除法，计算分子/分母的小数部分"""
    # 计算整数部分
    quotient = numerator // denominator
    remainder = numerator % denominator
    
    # 计算小数部分
    decimal_digits = []
    for _ in range(digits + 10):  # 多计算10位用于四舍五入
        if remainder == 0:
            break
        remainder *= 10
        digit = remainder // denominator
        decimal_digits.append(str(digit))
        remainder = remainder % denominator
    
    # 确保有足够的位数
    while len(decimal_digits) < digits + 1:
        decimal_digits.append('0')
    
    return ''.join(decimal_digits)

def save_pi_to_file(pi_decimal, precision_digits, computation_time, filename=None):
    """将圆周率结果保存到文件"""
    if filename is None:
        filename = f"pi_{precision_digits}_digits.txt"
    
    # 使用统一的目录获取方法
    exe_dir = os.path.dirname(sys.argv[0])
    filepath = os.path.join(exe_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"圆周率 π 的前 {precision_digits} 位小数\n")
            f.write(f"计算时间: {computation_time:.2f} 秒\n")
            f.write(f"计算日期: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
            f.write(f"3.{pi_decimal}\n")
        
        print(f"✓ 结果已保存到: {filepath}")
        return True
    except Exception as e:
        print(f"⚠ 保存文件时出错: {e}")
        return False

def get_user_precision():
    """获取用户输入的计算精度"""
    while True:
        try:
            print("\n" + "="*50)
            print("圆周率计算程序")
            print("="*50)
            print("请输入要计算的圆周率位数 (20-100000):")
            print("注意: 位数越多，计算时间越长，内存消耗越大")
            print("推荐: 100-10000位")
            
            user_input = input("计算位数: ").strip()
            
            if not user_input:
                print("使用默认值: 1000 位")
                return 1000
                
            precision = int(user_input)
            
            if precision < 20:
                print("位数必须大于或等于20，使用默认值: 1000 位")
                return 1000
            elif precision > 100000:
                print("警告: 位数超过10000可能导致计算机无响应!")
                confirm = input("确定要继续吗? (y/N): ").strip().lower()
                if confirm == 'y':
                    return precision
                else:
                    print("请重新输入")
                    continue
            else:
                return precision
                
        except ValueError:
            print("请输入有效的数字!")
        except KeyboardInterrupt:
            print("\n程序已取消")
            sys.exit(0)

def estimate_terms_needed(precision_digits):
    """根据目标精度估算需要的级数项数"""
    # Chudnovsky级数每项大约增加14位精度
    # 这是一个经验公式，可以根据需要调整
    base_terms = max(10, precision_digits // 14)
    # 添加一些安全余量
    return min(base_terms + 10, 100000)  # 限制最大项数

def main():
    # 先获取用户输入，然后再开始计时
    try:
        precision_digits = get_user_precision()
        
        # 现在开始计时
        computation_start_time = time.time()
        
        # 根据精度估算需要的级数项数
        total_terms = estimate_terms_needed(precision_digits)
        
        print(f"\n开始计算圆周率，目标精度: {precision_digits} 位小数")
        print(f"使用 {mp.cpu_count()} 个CPU核心")
        print(f"计算级数项数: {total_terms}")
        
        # 内存检查
        memory_threshold = max(1.0, precision_digits / 10000)  # 根据精度调整内存阈值
        if not check_memory_usage(memory_threshold):
            response = input("内存可能不足，是否继续？(y/n): ")
            if response.lower() != 'y':
                print("计算已取消")
                return
        
        # 准备多进程计算范围
        num_cores = min(mp.cpu_count(), total_terms)  # 避免创建过多进程
        chunk_size = (total_terms + num_cores - 1) // num_cores
        ranges = [
            (i * chunk_size, min((i + 1) * chunk_size - 1, total_terms))
            for i in range(num_cores)
        ]
        
        print("正在进行多进程级数计算...")
        pool = mp.Pool(processes=num_cores)
        results = pool.starmap(compute_pi_terms, ranges)
        pool.close()
        pool.join()
        
        # 再次检查内存
        if not check_memory_usage(0.5):
            print("内存严重不足，可能影响计算精度")
        
        print("合并多进程结果...")
        # 合并所有进程的结果
        S_num, S_den = results[0]
        for i in range(1, len(results)):
            num2, den2 = results[i]
            # 通分相加: a/b + c/d = (a*d + b*c)/(b*d)
            new_num = S_num * den2 + num2 * S_den
            new_den = S_den * den2
            # 约分
            gcd_val = math.gcd(abs(new_num), new_den)
            if gcd_val > 1:
                S_num = new_num // gcd_val
                S_den = new_den // gcd_val
            else:
                S_num, S_den = new_num, new_den
        
        print("计算高精度平方根...")
        # 计算 sqrt(640320) 到足够精度
        sqrt_precision = precision_digits + 20  # 额外精度
        sqrt_val = high_precision_sqrt(640320, sqrt_precision)
        
        print("进行最终高精度除法...")
        # 计算 π = (640320 * sqrt(640320)) / (12 * S)
        # 分子: 640320 * sqrt_val * S_den
        numerator_val = 640320 * sqrt_val * S_den
        # 分母: 12 * S_num * 10^sqrt_precision (因为sqrt_val被放大了10^sqrt_precision倍)
        denominator_val = 12 * S_num * (10**sqrt_precision)
        
        # 高精度除法获取小数部分
        decimal_str = high_precision_division(numerator_val, denominator_val, precision_digits + 1)
        
        # 格式化和四舍五入
        pi_decimal = decimal_str[:precision_digits]
        round_digit = int(decimal_str[precision_digits]) if len(decimal_str) > precision_digits else 0
        
        # 处理四舍五入
        if round_digit >= 5:
            # 将小数部分转为整数并加1
            num_val = int(pi_decimal) + 1
            pi_decimal = str(num_val).zfill(precision_digits)
            # 处理进位溢出
            if len(pi_decimal) > precision_digits:
                pi_decimal = pi_decimal[1:]
        
        computation_end_time = time.time()
        computation_time = computation_end_time - computation_start_time
        
        # 输出结果
        print(f"\n圆周率的前{precision_digits}位：")
        print(f"3.{pi_decimal}")
        print(f"\n计算用时: {computation_time:.2f} 秒")
        
        # 验证结果（前20位）
        known_pi_start = "14159265358979323846"
        if pi_decimal.startswith(known_pi_start):
            print("✓ 结果验证通过（前20位正确）")
            
            # 保存结果到文件
            save_pi_to_file(pi_decimal, precision_digits, computation_time)
        else:
            print("⚠ 结果验证失败，前20位不匹配")
            # 即使验证失败也保存结果（供调试用）
            save_pi_to_file(pi_decimal, precision_digits, computation_time, "pi_verification_failed.txt")
        
        input("按回车键退出...")
            
    except MemoryError:
        computation_end_time = time.time()
        computation_time = computation_end_time - computation_start_time if 'computation_start_time' in locals() else 0
        print(f"\n❌ 内存不足错误！计算已终止")
        print(f"已运行时间: {computation_time:.2f} 秒")
        print("建议：减少精度设置或关闭其他程序")
        input("按回车键退出...")
        
    except Exception as e:
        computation_end_time = time.time()
        computation_time = computation_end_time - computation_start_time if 'computation_start_time' in locals() else 0
        print(f"\n❌ 计算过程中发生错误: {e}")
        print(f"已运行时间: {computation_time:.2f} 秒")
        input("按回车键退出...")

if __name__ == '__main__':
    main()