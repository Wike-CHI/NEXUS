import sys
import os

# 将项目根目录添加到 Python 路径中，以便能够正确导入模块
# 这是为了确保无论从哪里运行 main.py，都能找到 nexus 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nexus.core.command_router import GeminiRouter
from nexus.core.safe_executor import execute_safe_command

def main():
    """
    NEXUS 项目的主入口函数。
    """
    # 实例化命令路由器
    # 它会自动加载 'configs/config.yaml' 配置文件
    router = GeminiRouter()
    print("NEXUS 运行中... 输入 'exit' 或 'quit' 退出")
    print("-" * 20)

    while True:
        try:
            # 从用户处获取输入
            user_input = input("请输入命令 > ")

            # 检查退出条件
            if user_input.lower() in ['exit', 'quit']:
                print("NEXUS 已退出。")
                break
            
            # 将用户输入（自然语言）转换为命令
            command = router.nl_to_command(user_input)

            # 如果命令为空字符串，则表示转换失败或无需执行
            if not command:
                print("无法识别或转换命令，请重试。")
                continue

            # 使用安全执行器执行命令
            print(f"正在执行: {command}")
            result = execute_safe_command(command)
            
            # 打印执行结果
            print("--- 执行结果 ---")
            print(result)
            print("------------------\n")

        except KeyboardInterrupt:
            # 允许用户通过 Ctrl+C 退出
            print("\nNEXUS 已强制退出。")
            break
        except Exception as e:
            # 捕获其他潜在错误
            print(f"发生未知错误: {e}")

if __name__ == "__main__":
    # 创建安全执行器需要的白名单目录，如果不存在的话
    if not os.path.exists("e:/NEXUS/docs"):
        os.makedirs("e:/NEXUS/docs")
    if not os.path.exists("e:/NEXUS/workspace"):
        os.makedirs("e:/NEXUS/workspace")
    main()