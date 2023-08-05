<%page args="makoGlobal, projectMetadata, params, niceParameterNames, files,
                blueprints"/>

<%
    domain = "servertribe.com"
    shields = "https://img.shields.io"
    docsBadge = f"{shields}/badge/docs-latest-brightgreen.svg"
    docsLink = f"http://doc.{domain}"
    chatBadge = f"{shields}/discord/844971127703994369"
    chatLink = f"http://discord.{domain}"
    videosBadge = f"{shields}/badge/videos-watch-brightgreen.svg"
    videosLink = f"https://www.youtube.com/@servertribe"
    downloadBadge = f"{shields}/badge/download-latest-brightgreen.svg"
    downloadLink = f"https://www.{domain}/community-edition/"
%>

[![Docs](${docsBadge})](${docsLink})
[![Discord](${chatBadge})](${chatLink})
[![Docs](${videosBadge})](${videosLink})
[![Generic badge](${downloadBadge})](${downloadLink})

# ${projectMetadata.name}

${projectMetadata.makeCommentMarkdown(topHeaderNum=2)}

<%include file="ProjectReadmeAttune.md.mako" args=""/>

<%include file="ProjectReadmeCloneInstructions.md.mako" args=""/>

<%include file="ProjectReadmeBlueprints.md.mako" args="blueprints=blueprints"/>

<%include file="ProjectReadmeParameters.md.mako" args="params=params, niceParameterNames=niceParameterNames"/>

<%include file="ProjectReadmeFiles.md.mako" args="files=files"/>

<%include file="ProjectReadmeContribute.md.mako" args=""/>

---

**Thank you**
