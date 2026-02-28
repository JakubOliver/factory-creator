# Notes to mindmap representation

Personally I am using xmind for mindmap, but .xmind file is pseudo binary, so it would not be best to store it in git repository. Therefore, via convertor to json (https://github.com/tobyqin/xmindparser) I create json representation which is more suitable for git.

## Commands

`pip install xmindparser`

`xmindparser your.xmind -json`