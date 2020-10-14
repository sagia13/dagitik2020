"""
Dağıtık sistemler Odev01
Ali Kaan Özden 16401781

"""

while True:
    try:
        soru_sayisi = input("Kaç tane soru sorulsun? ")
        soru_sayisi_int = int(soru_sayisi)
        break
    except:
        print("lütfen tam sayı giriniz. \n")
        continue


i = 0
flag = 0
flag2 = 0
flag3 = 0
ogrenci = {}

while i != soru_sayisi_int:

    if flag == 1:
        print("lütfen numara ve yaşınızı sayı olarak, adınızı ve soyadınızı sözcük olarak yazın. \n")
        flag = 0
    if flag2 == 1:
        print("Bu numara ile kayıtlı bir öğrenci zaten bulunmaktadır. \n")
        flag2 = 0
    if flag3 == 1:
        print("Yeterli sayıda veri verilmedi. \n")
        flag3 = 0
    
    cevap = input("Lütfen numara, isim, soyisim ve yaşınızı sırasıyla aralarda boşluk bırakarak yazınız: ")
    input_listesi = cevap.split(" ")
    uzunluk = len(input_listesi)
    
    if uzunluk > 4:
        fark = uzunluk - 4
    if uzunluk < 4:
        flag3 = 1
        continue
    
    try:
        numara = int(input_listesi[0])
        yas = int(input_listesi.pop())
    except:
        flag = 1
        continue
    
    try :
        isim = int(input_listesi[1:-1])
        flag = 1
        continue
    except:
        pass
    
    try :
        soyisim = int(input_listesi[-1])
        print("çalıştı")
        flag = 1
        continue
    except:
        pass
    
    isim = input_listesi[1:-1]
    soyisim = input_listesi.pop()
     
    if numara in ogrenci.keys():
        flag2 = 1
        continue
    info_tuple = (isim,soyisim,yas)
    ogrenci[numara] = info_tuple
    
    i = i + 1

print(ogrenci)
    


