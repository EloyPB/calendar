import json

figures = []

while True:
    print('\nAdding new figure...')
    figure = []
    while True:
        print('\nAdding new plot...')
        field = input('\nField: ')
        var_type = input('Type: ')
        color = input('Color: ')
        new_plot = {'field': field, 'type': var_type, 'color': color}
        figure.append(new_plot)
        command = input('\nFinished with this figure? y/n ')
        if command == 'y':
            break
    figures.append(figure)
    command = input('\nFinished with all the figures? y/n ')
    if command == 'y':
        break

with open('plots.txt', 'w') as f:
    json.dump(figures, f, indent=4, separators=(',', ': '), ensure_ascii=False)
