import pandas as pd

class BAlbuns:
    def __init__(self):
        #Criação de dicionário com a lista de Albuns dos Beatles
        self.balbums={'Name': ['1-Please Please Me',
                      '2-With The Beatles',
                      '3-A Hard Day\'s Night', 
                      '4-Beatles for Sale', 
                      '5-Help!', 
                      '6-Rubber Soul',
                      '7-Revolver',
                      '8-Sgt. Pepper\'s Lonely Hearts Club Band',
                      '9-Magical Mystery Tour',
                      '10-White Album',
                      '11-Yellow Submarine',
                      '12-Abbey Road',
                      '13-Let It Be'],
                    'Year': [1963, 1963, 1964, 1964, 1965, 1965, 1966, 1967, 1967, 1968, 1969, 1969, 1970]}
    def show_albuns(self):
        #Converter dicionário numa Dataframe em Pandas
         print(f"=== Welcome! This is the list of The Beatles's albums ===".center(50))
         print(f"=== I love The Beatles!! ===".center(50))
         return pd.DataFrame(self.balbums)