# BCV library context

This library must be executed with a accessible `.config.json` :

```json
{ 
  "day": 2,
  "scriptsVersion": "V3"
}
```

### How to use

```python
import bcvContext as bcv

bcv.scriptContext(fileName)

bcv.dayContext(m,filename)

bcv.getRawfile()
```