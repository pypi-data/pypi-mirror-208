# Connectivly

To get started:

``` bash
pip install connectivly
```

``` python
from connectivly import Connectivly

client = Connectivly('API-KEY', 'YOUR-URL')
session = client.get_login_session('session-id')
```