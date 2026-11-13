from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        result = []
        for distributore in self._distributori: # Prendi un distributore alla volta
            #Per il distributore che stiamo guardando in quel momento, va a prendere tutti i prezzi registrati durante tutto l'anno.
            prezzi = distributore.get_prezzi()
            lista_prezzi = [] #nuovo "cestino vuoto" temporaneo--> dentoro ci metteremo solo i prezzi che appartengono al mese che ci interessa
            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    lista_prezzi.append(prezzo.prezzo_litro)
            media = sum(lista_prezzi) / len(lista_prezzi)
            result.append((distributore.nome, media))
            #print(f"DEBUG - Risultato calcolato: {result}")  # <--- Aggiungi questo
            return result

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO
        # Cosa fa: L'omino ha riempito tutti e 7 i giorni del calendario. È arrivato alla fine del viaggio.
        # Il controllo: Prende la spesa totale fatta su questa strada e la confronta con il record precedente (self.__costo_ottimo).
        # Se questa strada è più economica della precedente (o se è la prima volta che arriviamo in fondo, indicato da -1),
        # allora l'omino dice: "Evviva! Ho trovato un nuovo record!", si salva il costo e si ricopia la sequenza dei distributori vincenti. Poi fa marcia indietro (return).

        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for distributore in self._distributori: #Per il giorno in cui si trova (es. Giorno 1), l'omino guarda tutti i distributori disponibili (il Distributore A e il Distributore B) e decide di provarli uno alla volta.
            prezzo_litro = prezzi_settimana[distributore.id][giorno - 1]
            costo_giornaliero = prezzo_litro * 100

            #Il prezzo della benzina: Prende il prezzo al litro di quel distributore in quel giorno e lo moltiplica per 100 litri.
            # La multa per il cambio: Guarda dove ha fatto rifornimento il giorno prima (ultimo_distributore). Se oggi ha cambiato distributore rispetto a ieri, aggiunge 5€ di multa allo spostamento.
            # Il totale parziale: Somma questa spesa del giorno alla spesa totale accumulata nei giorni scorsi (nuovo_costo).
            # Si segna la scelta: Aggiunge temporaneamente questo distributore alla sua lista del percorso (sequenza_parziale.append)
            if ultimo_distributore is not None and distributore.id != ultimo_distributore:
                costo_giornaliero += 5

            nuovo_costo = costo_corrente + costo_giornaliero
            sequenza_parziale.append(distributore.id)

            #Se la spesa che ha accumulato fino a questo momento è già più alta del record economico che aveva trovato in precedenza, si ferma. Non ha senso continuare a esplorare una strada che è già troppo costosa.
            # Se invece il costo è ancora competitivo, l'omino fa una chiamata a se stesso (self.__ricorsione(...)) per passare al giorno successivo (giorno + 1).
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                self.__ricorsione(sequenza_parziale, giorno + 1, distributore.id, nuovo_costo, prezzi_settimana)

            # finito di esplorare una strada fino in fondo (o l'ha scartata perché troppo costosa), deve tornare indietro per provare l'altra opzione (se prima aveva provato il Distributore A, adesso deve pulire la casella e provare il Distributore B).
            # Questo ripulire la scelta fatta si chiama backtracking.
            sequenza_parziale.pop()



    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        prezzi_primi_gg_mese = {} #dizionario vuoto che alla fine conterrà i prezzi ordinati per ciascun distributore.
        for distributore in self._distributori:
            #lista di tutti i prezzi di un singoloo distributore
            prezzi = distributore.get_prezzi()
            prezzi.sort(key=lambda prezzo:prezzo.data) #Ordina i prezzi in base alla data, dal primo giorno dell'anno fino all'ultimo. Questo è importantissimo per fare in modo che i giorni siano in fila dal 1° al 7° in ordine cronologico.
            # lista dei prezzi del mese che viene aggiornata se si verifica la condizione
            lista_prezzi = []
            for prezzo in prezzi:
                if prezzo.data.month == mese and 1<= prezzo.data.day <= 7: # verifica del mese
                    lista_prezzi.append(prezzo.prezzo_litro) #Prende il prezzo al litro di quel giorno e lo infila nel cestino temporaneo
            prezzi_primi_gg_mese[distributore.id] = lista_prezzi #Quando ha trovato tutti e 7 i prezzi dei primi giorni, li collega all'ID del distributore dentro al nostro grande dizionario (prezzi_primi_gg_mese)
        return prezzi_primi_gg_mese