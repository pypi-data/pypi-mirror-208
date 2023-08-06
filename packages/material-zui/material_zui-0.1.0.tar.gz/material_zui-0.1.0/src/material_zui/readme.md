# Modules

<ol>
  <li>bard</li>
  <li>compress</li>
  <li>crawl</li>
  <li>crontab</li>
  <li>date_time</li>
  <li>env</li>
  <li>gpt</li>
  <li>
    image
    <ul>
      <li>grayscale</li>
      <li>colorization</li>
      <li>sketch</li>
      <li>transparent background</li>
      <li>upscale</li>
      <li>convert to jpg/png</li>
    </ul>
  </li>
  <li><a href="#log">Log</a></li>
  <li>regex</li>
  <li>replicate: AI Platform API</li>
  <li>telegram_bot</li>
  <li>validate</li>
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

<!-- - Result:
  ![](../../static/img/doc/log1.png) -->

# Package

- https://pypi.org/project/material-zui
