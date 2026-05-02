import csv

def load_coordinates(arquivo='coordinates.txt'):
    """Carrega coordenadas do arquivo"""
    points = []
    with open(arquivo, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line == ',':
                continue
            try:
                partes = line.split(',')
                lat = float(partes[0].strip())
                lon = float(partes[1].strip())
                points.append({
                    'lat': lat,
                    'lon': lon,
                    'popupContent': f"Coordenada: {lat:.4f}, {lon:.4f}"
                })
            except (ValueError, IndexError):
                continue
    return points

def load_butecos(points, arquivo='butecos_bh.csv'):
    """Carrega butecos do CSV e associa às coordenadas"""
    butecos = []
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for i, row in enumerate(reader):
            butecos.append({
                'name': row['name'].strip(),
                'address': row['address'].strip(),
                'lat': points[i]['lat'],
                'lon': points[i]['lon']
            })
    return butecos
