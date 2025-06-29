import subprocess
import os

# 路径白名单，只允许在这些目录下执行操作
# 使用 os.path.abspath 转换为绝对路径以进行可靠的比较
ALLOWED_PATHS = [
    os.path.abspath("e:/NEXUS/docs"),
    os.path.abspath("e:/NEXUS/workspace")
]

# 高风险命令列表，这些命令将被拦截
FORBIDDEN_COMMANDS = ['rm', 'del', 'format', 'rd', 'rmdir']

def is_safe(cmd: str) -> (bool, str):
    """
    检查命令是否安全。

    Args:
        cmd: 待检查的系统命令。

    Returns:
        一个元组，第一个元素是布尔值表示是否安全，第二个是原因。
    """
    # 1. 检查是否包含高风险命令
    command_parts = cmd.split()
    if command_parts and command_parts[0].lower() in FORBIDDEN_COMMANDS:
        # 简单的删除命令（如 del a.txt）可能需要更复杂的逻辑来判断路径
        # 这里为了安全，暂时一刀切拦截
        return False, f"高风险命令 '{command_parts[0]}' 被禁止。"

    # 2. 检查路径是否在白名单内
    # 这是一个简化的检查，它要求命令中如果包含路径，必须是白名单内的路径
    # 注意：这个检查逻辑比较初级，例如 `dir c:\` 仍然会被允许，因为它不直接包含白名单路径
    # 更完善的方案需要解析命令中的所有路径参数并逐一检查
    has_path_argument = any(os.path.exists(part) for part in command_parts)
    if has_path_argument:
        is_path_allowed = any(path in cmd for path in ALLOWED_PATHS)
        if not is_path_allowed:
            return False, "命令试图访问不在白名单内的路径！"

    return True, "命令安全"

def execute_safe_command(cmd: str):
    """
    在安全检查通过后执行命令。

    Args:
        cmd: 待执行的系统命令。

    Returns:
        命令的执行结果或错误信息。
    """
    if not cmd:
        return "错误：没有提供任何命令。"

    is_command_safe, reason = is_safe(cmd)
    if not is_command_safe:
        return f"错误：{reason}"

    try:
        # 执行命令，并捕获输出
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout or result.stderr
    except subprocess.CalledProcessError as e:
        # 捕获执行过程中的错误
        return f"命令执行失败: {e.stderr}"