from onvif.util import normalize_url


def test_normalize_url():
    assert normalize_url("http://1.2.3.4:80") == "http://1.2.3.4:80"
    assert normalize_url("http://1.2.3.4:80:80") == "http://1.2.3.4:80"
    assert normalize_url("http://[:dead:beef::1]:80") == "http://[:dead:beef::1]:80"
