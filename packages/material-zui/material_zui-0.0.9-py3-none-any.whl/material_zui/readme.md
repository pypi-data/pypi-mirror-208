# Modules

<ol>
  <li>Crawl</li>
  <li>
    Image
    <ul>
      <li>grayscale</li>
      <li>colorization</li>
      <li>sketch</li>
      <li>transparent background</li>
      <li>upscale</li>
      <li>convert to jpg/png</li>
    </ul>
  </li>
  <li>Language Model</li>
  <li>Regex</li>
  <li>Log</li>
  <li>Replicate: AI Platform API</li>
  <li>Telegram Bot</li>
  <li>Validate</li>
</ol>

# Log

- Example:

```py
from material_zui.log import debug, info, warning, error, critical, printTable

debug('This is a debug message')
info('This is an info message')
warning('This is a warning message')
error('This is an error message')
critical('This is a critical message')

printTable({
    'Name': ['Alice', 'Bob', 'Charlie', 'Dave'],
    'Age': [25, 31, 35, 19],
    'Score': [85, 94, 76, 95]
})
```

- Result:
  ![Alt text](../../static/img/doc/log1.png)

# Package

- https://pypi.org/project/material-zui
