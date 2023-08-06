from . import colors

qss = f'''
#SearchBar {{
    background-color: {colors.LAYER_3};
    font-size: 18px;
    padding: 5px;
    color: {colors.TEXT_PRIMARY};
    border: none;
}}

#SearchBarPopup {{
    background-color: {colors.LAYER_1};
    border: none;
    font-size: 20px;
    font-weight: bold;
    color: {colors.TEXT_PRIMARY};
}}

QListView::item:hover {{
    background-color: {colors.LAYER_5};
}}
'''
