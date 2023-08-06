def test_asd(pypi):
    import urllib.request

    print("asdasdds")
    asd = urllib.request.urlopen(f"{pypi}/package")
    print(asd.status)
    print(asd.read().decode("utf-8"))
    pass
