from fixerio import fixerio


def main():
    test = fixerio.Fixerio()
    response = test.convert(20, base='USD', dest='EUR')
    print(response, end='\n\n')
    response = test.get_rates(date='2010-12-31')
    print(response, end='\n\n')
    # print(test._cache)
    response = test.convert(1000.0, 'EUR', date='2010-12-31')
    print(response, end='\n\n')
    response = test.convert(1000.0, 'JPY', date='2010-12-31')
    print(response, end='\n\n')
    response = test.convert(1000.0, base='JPY', dest='JPY')
    print(response, end='\n\n')
    response = test.convert(1000.0, base='EUR', dest='JPY')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', base='USD')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', symbols='JPY')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', base='USD', symbols='EUR, JPY')
    print(response, end='\n\n')


if __name__ == '__main__':
    main()
