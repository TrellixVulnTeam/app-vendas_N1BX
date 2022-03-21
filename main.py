from urllib import request
from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFirebase
from bannervendedor import BannerVendedor

# banco de dados: https://console.firebase.google.com/
# file onde contém a parte visual da página - *comentar bloco atalho: ctrl + /
GUI = Builder.load_file("main.kv")

# parte lógica do programa - padrão para iniciar o app


class MainApp(App):

    id_usuario = 1

    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        # carregar as fotos de perfil
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]

        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        # carrega as infos do usuario
        self.carregar_infos_usuario()



    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()

            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
            #pegar informações do usuario
            requisicao = requests.get(
                f"https://aplicativovendas-6d2e9-default-rtdb.firebaseio.com/{self.local_id}.json")
            requisicao.dic = requisicao.json()

            # preencher foto de perfil
            avatar = requisicao.dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            #preencher id unico
            id_vendedor = requisicao.dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"Seu ID Único: {id_vendedor}"


            #preencher total de vendas
            total_vendas = requisicao.dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            #preencher equipe
            self.equipe = requisicao.dic['equipe']



            # preencher lista de vendas
            try:
                vendas = requisicao.dic['vendas'][1:]
                self.vendas = vendas 
                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for venda in vendas:
                   banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                        produto=venda['produto'], foto_produto=venda['foto_produto'],
                                        data=venda['data'], preco=venda['preco'], unidade=venda['unidade'],
                                        quantidade=venda['quantidade'])

                   lista_vendas.add_widget(banner)


            except:
                pass

            #preencher equipe de vendedores
            equipe = requisicao.dic['equipe']
            lista_equipe = equipe.split(",")

            pagina_listavendedores = self.root.ids["listarvendedorespage"]
            lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)


            self.mudar_tela("homepage")
        except:
            pass






    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela



    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"        


        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://aplicativovendas-6d2e9-default-rtdb.firebaseio.com/{self.local_id}.json", data=info)

        self.mudar_tela("ajustespage")

    

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendas-6d2e9-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        print(requisicao_dic)
        
        pagina_adicionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionarvendedor.ids["mensagem_outrovendedor"]

        if requisicao_dic == {}:
            mensagem_texto.text = "Usuário não encontrado"
        else: 
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendas-6d2e9-default-rtdb.firebaseio.com/{self.local_id}.json", data=info)
                mensagem_texto.text = "Vendedor adicionado com sucesso!"

                # adicionar um novo bannner na lista de vendedores
                pagina_listavendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)            
                



MainApp().run()





