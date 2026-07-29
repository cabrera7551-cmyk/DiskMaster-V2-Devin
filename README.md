# DiskMaster V2

Gestor inteligente de almacenamiento — **interfaz visual de demostracion** (Electron).

Identidad visual "Terminal Blackout Blue": fondo `#000000`, azul `#2E8FE0`, tipografia monoespaciada.

## Estado actual

Solo interfaz y navegacion con **datos estaticos de demostracion**. No hay analisis real de discos,
exploracion del sistema de archivos ni modificaciones del sistema.

## Requisitos

- Node.js 18 o superior

## Ejecucion

```bash
npm install
npm start
```

## Estructura

```
package.json        configuracion y script "start"
src/main.js         proceso principal de Electron (BrowserWindow)
src/preload.js      preload minimo
ui/index.html       las 7 pantallas
ui/css/styles.css   estilos y paleta (variables CSS)
ui/js/app.js        navegacion SPA
```

## Pantallas

`~/panel` · `~/analisis` · `~/explorar` · `~/gestionar` · `~/recomendaciones` · `~/ajustes` · `~/historial`
