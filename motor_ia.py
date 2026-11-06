"""Motor de Inteligencia Artificial para análisis futbolístico y clasificación semafórica.
Soporta modelos de Google Gemini (SDK google-genai) y OpenAI con salida JSON estructurada y temperatura 0.
"""
import json
import os
import re
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

# Base de conocimiento enriquecida para los 20 jugadores oficiales
BASE_JUGADORES = {
    "j001": {
        "nombre": "Lionel Messi",
        "pais": "Argentina",
        "titulos": ["Copa del Mundo 2022", "8 Balones de Oro", "4 UEFA Champions League", "2 Copas América"],
        "rendimiento_historico": "Sobresaliente / Leyenda Absoluta",
        "color_default": "verde"
    },
    "j002": {
        "nombre": "Cristiano Ronaldo",
        "pais": "Portugal",
        "titulos": ["5 UEFA Champions League", "5 Balones de Oro", "Eurocopa 2016", "Máximo goleador histórico del fútbol profesional"],
        "rendimiento_historico": "Sobresaliente / Goleador Histórico",
        "color_default": "verde"
    },
    "j003": {
        "nombre": "Neymar",
        "pais": "Brasil",
        "titulos": ["Copa Libertadores con Santos", "UEFA Champions League con Barcelona", "Oro Olímpico Río 2016", "Máximo goleador con Brasil"],
        "rendimiento_historico": "Alto pero condicionado por lesiones recurrentes",
        "color_default": "amarillo"
    },
    "j004": {
        "nombre": "Kylian Mbappé",
        "pais": "Francia",
        "titulos": ["Copa del Mundo 2018", "Bota de Oro Mundial 2022", "Múltiples Ligue 1", "UEFA Nations League 2021"],
        "rendimiento_historico": "Élite mundial con velocidad y definición descomunales",
        "color_default": "verde"
    },
    "j005": {
        "nombre": "Erling Haaland",
        "pais": "Noruega",
        "titulos": ["UEFA Champions League (Triplete con Man City)", "Bota de Oro Europea", "Premier League"],
        "rendimiento_historico": "Goleador élite implacable en el área",
        "color_default": "verde"
    },
    "j006": {
        "nombre": "Vinícius Júnior",
        "pais": "Brasil",
        "titulos": ["2 UEFA Champions League (gol en final)", "LaLiga de España", "Mundial de Clubes de la FIFA"],
        "rendimiento_historico": "Extremo desequilibrante determinante en partidos grandes",
        "color_default": "verde"
    },
    "j007": {
        "nombre": "Mohamed Salah",
        "pais": "Egipto",
        "titulos": ["UEFA Champions League 2019", "Premier League", "3 Botas de Oro de Premier League"],
        "rendimiento_historico": "Constancia goleadora y asistencias de máximo nivel",
        "color_default": "verde"
    },
    "j008": {
        "nombre": "Robert Lewandowski",
        "pais": "Polonia",
        "titulos": ["UEFA Champions League 2020", "The Best FIFA (2 veces)", "Múltiples Bundesligas y LaLiga"],
        "rendimiento_historico": "Delantero centro de época y rematador letal",
        "color_default": "verde"
    },
    "j009": {
        "nombre": "Luka Modrić",
        "pais": "Croacia",
        "titulos": ["6 UEFA Champions League", "Balón de Oro 2018", "Subcampeón del Mundo 2018 y Bronce 2022"],
        "rendimiento_historico": "Director de orquesta insustituible y vigencia legendaria",
        "color_default": "verde"
    },
    "j010": {
        "nombre": "Kevin De Bruyne",
        "pais": "Bélgica",
        "titulos": ["UEFA Champions League (Triplete)", "Múltiples Premier League", "Máximo asistente europeo"],
        "rendimiento_historico": "Visión de juego y precisión de pase top del siglo XXI",
        "color_default": "verde"
    },
    "j011": {
        "nombre": "Luis Suárez",
        "pais": "Uruguay",
        "titulos": ["Copa América 2011", "UEFA Champions League 2015", "2 Botas de Oro europeas"],
        "rendimiento_historico": "Delantero centro feroz y letal",
        "color_default": "verde"
    },
    "j012": {
        "nombre": "James Rodríguez",
        "pais": "Colombia",
        "titulos": ["Bota de Oro Mundial 2014", "2 UEFA Champions League", "Mejor jugador Copa América 2024"],
        "rendimiento_historico": "Talento técnico exquisito, a veces intermitente a nivel de clubes",
        "color_default": "amarillo"
    },
    "j013": {
        "nombre": "Luis Díaz",
        "pais": "Colombia",
        "titulos": ["FA Cup", "Carabao Cup", "Goleador Copa América 2021", "Primeira Liga"],
        "rendimiento_historico": "Desborde vertical y sacrificio físico notable",
        "color_default": "verde"
    },
    "j014": {
        "nombre": "Son Heung-min",
        "pais": "Corea del Sur",
        "titulos": ["Bota de Oro Premier League 2021-22", "Juegos Asiáticos Oro"],
        "rendimiento_historico": "Atacante versátil con gran pegada ambidiestra pero pocos títulos colectivos",
        "color_default": "amarillo"
    },
    "j015": {
        "nombre": "Sadio Mané",
        "pais": "Senegal",
        "titulos": ["Copa Africana de Naciones 2021", "UEFA Champions League 2019", "Premier League"],
        "rendimiento_historico": "Líder ofensivo, potencia y títulos continentales",
        "color_default": "verde"
    },
    "j016": {
        "nombre": "Pelé",
        "pais": "Brasil",
        "titulos": ["3 Copas del Mundo (1958, 1962, 1970)", "2 Copas Libertadores e Intercontinentales", "Más de 1000 goles"],
        "rendimiento_historico": "Rey del fútbol y pionero indiscutible",
        "color_default": "verde"
    },
    "j017": {
        "nombre": "Diego Maradona",
        "pais": "Argentina",
        "titulos": ["Copa del Mundo 1986", "2 Scudettos históricos con Napoli", "Copa UEFA"],
        "rendimiento_historico": "Genio inmortal, trascendencia absoluta con su selección",
        "color_default": "verde"
    },
    "j018": {
        "nombre": "Zinedine Zidane",
        "pais": "Francia",
        "titulos": ["Copa del Mundo 1998", "Eurocopa 2000", "UEFA Champions League 2002 (gol icónico)", "Balón de Oro"],
        "rendimiento_historico": "Elegancia, pausa y determinación en las finales más trascendentes",
        "color_default": "verde"
    },
    "j019": {
        "nombre": "Ronaldinho",
        "pais": "Brasil",
        "titulos": ["Copa del Mundo 2002", "UEFA Champions League 2006", "Balón de Oro 2005", "Copa Libertadores 2013"],
        "rendimiento_historico": "Magia pura e inventiva que redefinió el fútbol mundial",
        "color_default": "verde"
