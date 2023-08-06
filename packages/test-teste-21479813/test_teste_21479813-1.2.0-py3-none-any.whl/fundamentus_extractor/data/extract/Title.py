class Title:  
    def __init__(self, text, col1, col2, row) -> None:
        self.text = text
        self.col1 = col1
        self.col2 = col2
        self.row = row
        self.subtitles = []
    
    def find_subtitle(self, pos):
        possibles = []
        for subtitle in self.subtitles:
            if(pos <= subtitle.col2 and pos >= subtitle.col1):
                possibles.append(subtitle)

        if(len(possibles) == 0):
            return None
        
        max_title = max(possibles, key= lambda x: x.row)
        return max_title
