<%page args="params, niceParameterNames"/>
<%text>
## Parameters
</%text>

| Name | Type | Script Reference | Comment |
| ---- | ---- | ---------------- | ------- |
% for parameter in params:
| ${parameter.name} | ${niceParameterNames[parameter.type]} | `${parameter.textName}` | ${parameter.comment} |
% endfor
