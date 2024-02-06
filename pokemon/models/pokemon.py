# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import requests

class Pokemon(models.Model):
    _name = "pokemon"

    name = fields.Char("Name")
    url = fields.Char("URL")


    def cron_update_pokemon(self):
        r = requests.get('https://pokeapi.co/api/v2/pokemon/')
        posts = r.json()
        if posts.get("results"):
            for pokemon in posts.get("results"):
                dct_pokemon = {"name":pokemon.get("name"),
                                "url":pokemon.get("url")}
                print(dct_pokemon)
                pokemon_id = self.env["pokemon"].search([("name","=",pokemon.get("name")),("url","=",pokemon.get("url"))])
                if not pokemon_id:
                    pokemon_id.create(dct_pokemon)
    
    