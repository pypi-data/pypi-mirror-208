qss = f'''
#Popup {{
    background-color: rgba(255, 255, 255, 0.1);
}}

#PopupFrame {{
    background-color: #17212B;
    width: 400px;
    height: 200px;
    border-radius: 20px;
}}

#PopupMessageLbl {{
    color: white;
    font-size: 24px;
    background-color: transparent;
}}

#PopupOkBtn,
#PopupCancelBtn,
#PopupYesBtn,
#PopupNoBtn {{
    color: white;
    border: none;
    font-size: 18px; 
    border-radius: 5px;
    min-height: 40px;
}}

#PopupOkBtn,
#PopupYesBtn {{
    background-color: darkgreen;
}}

#PopupOkBtn:hover,
#PopupYesBtn:hover {{
    background-color: rgba(0, 255, 0, 0.5);
}}

#PopupCancelBtn,
#PopupNoBtn {{
    background-color: rgba(182, 0, 40, 1);
}}

#PopupCancelBtn:hover,
#PopupNoBtn:hover {{
    background-color: rgba(182, 0, 40, 0.5);
}}
'''
