#Rocolencion de Datos
def tomar_datos(owner, repo, max_pags=50, per_page=100):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    todos = []                      

    for pag in range(1, max_pags + 1):
        params = {
            "page": pag,
            "per_page": per_page,
            "state": "all"
        }
        print(f"▸ Página {pag}...")
        
        try:
            r = requests.get(url, params=params, timeout=12)
            r.raise_for_status()          
            
            items = r.json()
            if not items:                 
                print("  No hay más páginas → terminamos")
                break
                
            todos.extend(items)           
            print(f"    → {len(items)} elementos agregados (total: {len(todos)})")
            
            time.sleep(0.7)               
            
        except requests.exceptions.HTTPError as e:
            if r.status_code in (403, 429):
                print("¡Límite de peticiones alcanzado! (sin token solo ~60/hora)")
                print("Espera 30–60 min o usa un token personal")
            else:
                print(f"Error HTTP {r.status_code}: {e}")
            break
            
        except Exception as e:
            print(f"Error inesperado: {e}")
            break

    
    if not todos:
        print("No se descargó ningún elemento.")
        return pd.DataFrame()

 
    datos = []
    for i in todos:
        es_pr = "pull_request" in i               
        datos.append({
            "número": i.get("number"),
            "título": i.get("title", ""),
            "texto": i.get("body") or "",
            "estado": i.get("state"),
            "es_pr": es_pr,
            "tipo": "Pull Request" if es_pr else "Issue",
            "url": i.get("html_url", "")
        })

    df = pd.DataFrame(datos)
    
    
    total = len(df)
    prs = df['es_pr'].sum()
    print(f"\nTotal descargado: {total} elementos")
    print(f"Pull Requests: {prs} ({prs/total*100:.1f}% si total > 0)")
    print("Ejemplos de PRs (si existen):")
    print(df[df['es_pr'] == True][['número', 'título', 'tipo']].head(3))

  
    archivo = f"data/{repo}_issues_y_prs.csv"
    df.to_csv(archivo, index=False, encoding='utf-8')
    print(f"Guardado en: {archivo}")
    
    return df

    ##################################################################################
    
