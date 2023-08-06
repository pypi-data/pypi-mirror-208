<div align="center">
<h1>Somnium</h1>
Create beautiful artwork using the power of AI
</div>



<h2>Installation:</h2>

```bash
>>> python3 -m pip install somnium
```

<h2>Examples:</h2>

```python
>>> from somnium import Somnium

>>> # Get Styles UI
>>> print(Somnium.StylesGraph())

>>> # Get Styles
>>> s = Somnium.Styles()

>>> # Generate Artwork
>>> print(Somnium.Generate('Girl', s[list(s.keys())[0]]))
```
