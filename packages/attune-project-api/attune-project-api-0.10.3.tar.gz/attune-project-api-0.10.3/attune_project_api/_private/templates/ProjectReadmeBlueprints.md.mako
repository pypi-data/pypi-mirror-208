<%page args="blueprints"/>
<%text>
## Blueprints

This Project contains the following Blueprints.

</%text>
% for blueprint in blueprints:

<%text>###</%text> ${blueprint.name}

% if blueprint.comment:
${blueprint.makeCommentMarkdown(topHeaderNum=4)}
% endif
% endfor