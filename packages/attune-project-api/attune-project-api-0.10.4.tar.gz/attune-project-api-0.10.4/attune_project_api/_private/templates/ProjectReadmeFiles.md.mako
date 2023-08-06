<%page args="files"/>
<%text>
## Files
</%text>

| Name | Type | Comment |
| ---- | ---- | ------- |
% for file in files:
| ${file.name} | ${file.niceName} | ${file.comment} |
% endfor
