import pickle
from models import Merchant, Item
from crawler import start_async

def get_options(keywords, min_rating):
    print_results = False
    with open('pickle/merchants.pickle', 'rb') as f:
        merchants = pickle.load(f)

    itens = []
    for merchant_name, info in merchants.items():
        m = info['info']
        m_itens = info['itens']
        for item in m_itens:
            itens.append((m.name, m.distance, m.delivery_fee, m.user_rating, item.price, item.taxonomy, item.description, item.details))

    sorted_itens = sorted(itens, key=lambda element: (element[4]), reverse=False)
    min_rating = min_rating
    
    results = []
    for i in sorted_itens:
        try:
            if all(x in i[6].lower() for x in keywords) or all(x in i[7].lower() for x in keywords):
                if i[3] > min_rating:
                    results .append((f'nome: {i[0]}, NOTA - {i[3]:.2f}\n'
                    f'distancia (km: {i[1]}\n'
                    f'preço: {i[4]}\n'
                    f'descrição: {i[6]}\n'
                    f'detalhes: {i[7]}\n'))
                    results.append()
        except:
            pass

    
    if print_results:
        for i in results:
            print(i)
    
    return results

def pipeline(keywords, min_rating, latitude, longitude,):
    start_async(latitude, longitude)
    results = get_options(keywords, min_rating)
    return results

if __name__ == '__main__':
    results = get_options(['picanha'], 4.2)