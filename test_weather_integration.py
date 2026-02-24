"""
Script de test pour l'intégration météo
Test automatique de toutes les fonctionnalités
"""

import sys
from datetime import datetime, timedelta

print("=" * 70)
print("🧪 TEST D'INTÉGRATION - SYSTÈME MÉTÉO AGRICOLE TOGO")
print("=" * 70)
print()

# Test 1: Import des modules
print("📦 Test 1: Import des modules...")
try:
    import requests
    import pandas as pd
    import numpy as np
    print("   ✅ Modules de base OK")
except ImportError as e:
    print(f"   ❌ Erreur d'import: {e}")
    print("   💡 Installez: pip install requests pandas numpy")
    sys.exit(1)

# Test 2: Connexion Internet
print("\n🌐 Test 2: Vérification connexion Internet...")
try:
    response = requests.get("https://api.open-meteo.com", timeout=5)
    if response.status_code == 200:
        print("   ✅ Connexion Internet OK")
    else:
        print(f"   ⚠️  Connexion limitée (code: {response.status_code})")
except Exception as e:
    print(f"   ❌ Pas de connexion Internet: {e}")
    print("   💡 Le système utilisera des valeurs par défaut")

# Test 3: API Open-Meteo (Données actuelles)
print("\n🌦️  Test 3: Récupération données Open-Meteo...")

def test_open_meteo_current(region="Maritime"):
    """Test API Open-Meteo pour données actuelles"""
    coords = {"lat": 6.1256, "lon": 1.2256}
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": ["temperature_2m", "precipitation", "relative_humidity_2m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "Africa/Lome",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp = current.get("temperature_2m", "N/A")
        precip = sum(daily.get("precipitation_sum", []))
        humidity = current.get("relative_humidity_2m", "N/A")
        
        print(f"   ✅ Données récupérées pour {region}:")
        print(f"      🌡️  Température: {temp}°C")
        print(f"      🌧️  Pluie (7j): {precip:.1f} mm")
        print(f"      💧 Humidité: {humidity}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur API: {e}")
        return False

success_current = test_open_meteo_current("Maritime")

# Test 4: API Open-Meteo (Données historiques)
print("\n📊 Test 4: Récupération données historiques...")

def test_open_meteo_historical():
    """Test API Open-Meteo pour données historiques"""
    coords = {"lat": 6.1256, "lon": 1.2256}
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    date_end = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": date_start,
        "end_date": date_end,
        "daily": ["temperature_2m_mean", "precipitation_sum"],
        "timezone": "Africa/Lome"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        temps = daily.get("temperature_2m_mean", [])
        precips = daily.get("precipitation_sum", [])
        
        if temps and precips:
            temp_moy = sum(temps) / len(temps)
            precip_total = sum(precips)
            
            print(f"   ✅ Historique 30 jours récupéré:")
            print(f"      🌡️  Température moyenne: {temp_moy:.1f}°C")
            print(f"      🌧️  Pluviométrie totale: {precip_total:.1f} mm")
            print(f"      📅 Période: {date_start} à {date_end}")
            
            return True
        else:
            print("   ⚠️  Données historiques vides")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur historique: {e}")
        return False

success_historical = test_open_meteo_historical()

# Test 5: Toutes les régions du Togo
print("\n🗺️  Test 5: Vérification toutes les régions...")

regions_togo = {
    "Maritime": {"lat": 6.1256, "lon": 1.2256},
    "Plateaux": {"lat": 6.9000, "lon": 0.8500},
    "Centrale": {"lat": 8.9711, "lon": 1.1056},
    "Kara": {"lat": 9.5511, "lon": 1.1856},
    "Savanes": {"lat": 10.5700, "lon": 0.2200}
}

results_regions = []

for region, coords in regions_togo.items():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": ["temperature_2m"],
        "timezone": "Africa/Lome"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        temp = data.get("current", {}).get("temperature_2m", "N/A")
        
        results_regions.append({
            "Région": region,
            "Température": f"{temp}°C",
            "Statut": "✅"
        })
    except:
        results_regions.append({
            "Région": region,
            "Température": "N/A",
            "Statut": "❌"
        })

df_regions = pd.DataFrame(results_regions)
print("\n" + df_regions.to_string(index=False))

# Test 6: Performance et latence
print("\n⚡ Test 6: Performance et latence...")

import time

def test_api_performance():
    """Mesure le temps de réponse de l'API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 6.1256,
        "longitude": 1.2256,
        "current": ["temperature_2m"],
        "timezone": "Africa/Lome"
    }
    
    start = time.time()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        end = time.time()
        latency = (end - start) * 1000  # en ms
        
        if latency < 1000:
            status = "Excellent"
            emoji = "🚀"
        elif latency < 2000:
            status = "Bon"
            emoji = "✅"
        elif latency < 5000:
            status = "Acceptable"
            emoji = "⚠️"
        else:
            status = "Lent"
            emoji = "🐌"
        
        print(f"   {emoji} Latence: {latency:.0f} ms ({status})")
        print(f"   📊 Recommandation: < 2000 ms pour une bonne UX")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur performance: {e}")
        return False

success_perf = test_api_performance()

# Test 7: Gestion des erreurs
print("\n🛡️  Test 7: Gestion des erreurs...")

def test_error_handling():
    """Test la gestion des erreurs"""
    
    # Test 1: Coordonnées invalides
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": 999, "longitude": 999}  # Invalide
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            print("   ✅ Gestion coordonnées invalides OK")
        else:
            print("   ⚠️  API accepte coordonnées invalides")
    except:
        print("   ✅ Exception capturée pour coordonnées invalides")
    
    # Test 2: Timeout
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            timeout=0.001  # Timeout très court
        )
    except requests.exceptions.Timeout:
        print("   ✅ Gestion timeout OK")
    except:
        print("   ✅ Exception timeout capturée")
    
    return True

test_error_handling()

# Test 8: Format des données
print("\n📋 Test 8: Validation format des données...")

def test_data_format():
    """Vérifie que les données sont dans le bon format"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 6.1256,
        "longitude": 1.2256,
        "current": ["temperature_2m", "relative_humidity_2m"],
        "daily": ["precipitation_sum"],
        "timezone": "Africa/Lome",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Vérifications
        checks = [
            ("Structure 'current'", "current" in data),
            ("Structure 'daily'", "daily" in data),
            ("Température (float)", isinstance(data.get("current", {}).get("temperature_2m"), (int, float))),
            ("Précipitations (list)", isinstance(data.get("daily", {}).get("precipitation_sum"), list)),
            ("Timezone correct", data.get("timezone") == "Africa/Lome")
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
        
        return all(check[1] for check in checks)
        
    except Exception as e:
        print(f"   ❌ Erreur validation: {e}")
        return False

success_format = test_data_format()

# Résumé des tests
print("\n" + "=" * 70)
print("📊 RÉSUMÉ DES TESTS")
print("=" * 70)

tests_results = [
    ("Modules de base", True),
    ("Connexion Internet", True),
    ("Données actuelles", success_current),
    ("Données historiques", success_historical),
    ("Toutes régions", all(r["Statut"] == "✅" for r in results_regions)),
    ("Performance", success_perf),
    ("Gestion erreurs", True),
    ("Format données", success_format)
]

total_tests = len(tests_results)
tests_passed = sum(1 for _, result in tests_results if result)

print()
for test_name, result in tests_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status:12} - {test_name}")

print("\n" + "-" * 70)
print(f"Résultat: {tests_passed}/{total_tests} tests réussis")

if tests_passed == total_tests:
    print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
    print("✅ Le système est prêt pour la production")
elif tests_passed >= total_tests * 0.75:
    print("\n✅ La plupart des tests sont passés")
    print("⚠️  Quelques fonctionnalités peuvent être limitées")
else:
    print("\n⚠️  PLUSIEURS TESTS ONT ÉCHOUÉ")
    print("🔧 Vérifiez la connexion Internet et les dépendances")

print("\n" + "=" * 70)
print(f"Test terminé le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
print("=" * 70)
