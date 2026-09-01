import json

with open('C:/Users/welcome/.gemini/antigravity/brain/5cffc324-782f-4fc8-8314-b785425eca18/.system_generated/logs/transcript_full.jsonl', encoding='utf-8') as f:
    for line in f:
        if 'write_to_file' in line:
            try:
                data = json.loads(line)
                calls = data.get('tool_calls', [])
                for c in calls:
                    args = c.get('args', {})
                    target = args.get('TargetFile', '').replace('\\', '/').strip('"').strip("'")
                    if 'engine/models/' in target or 'engine/data/' in target:
                        content = args.get('CodeContent', '')
                        if content.startswith('"') and content.endswith('"'):
                            try:
                                content = json.loads(content)
                            except:
                                pass
                        with open(target, 'w', encoding='utf-8') as out:
                            out.write(content)
                        print(f"Recovered {target}")
            except Exception as e:
                pass
