import re

filepath = r'd:\workspace\practice\gitHubProject\MaxKB4j-master\docs\面试题库\Java AI应用大全\Java AI应用面试题库大全-主文档.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all ```java ... ``` code blocks
# The pattern matches from ```java to the next ``` that ends the block
pattern = r'(^|\n)```java\n(.*?)\n```($|\n)'

def wrap_code(match):
    prefix = match.group(1)
    code = match.group(2)
    suffix = match.group(3)
    # Skip if already wrapped inside details
    return f'{prefix}<details>\n<summary>📘 点击展开代码</summary>\n\n```java\n{code}\n```\n\n</details>{suffix}'

new_content = re.sub(pattern, wrap_code, content, flags=re.DOTALL)

# Count results
before_count = len(re.findall(r'^```java\n', content, re.MULTILINE))
after_details = new_content.count('<details>')
after_code = len(re.findall(r'^```java\n', new_content, re.MULTILINE))

print(f'原始代码块数: {before_count}')
print(f'折叠块数量: {after_details}')
print(f'包裹后代码块数: {after_code}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('完成！')
