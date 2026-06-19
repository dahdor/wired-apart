### 📊 Estructura de la Presentación (8:30 min)
**Tema:** *Wired Apart: El coste de la infancia digital.*
**Estructura narrativa:** Contexto → Cambio en el tiempo → Contraste → Outliers → Causa raíz → Solución → Llamado a la Acción.

---

### 🎙️ GUION DE LA PRESENTACIÓN

**(0:00 - 1:15) El Gancho y el Contexto (Zoom Out)**
*[Diapositiva 1: Título "Wired Apart". Imagen partida: a la izquierda, niños jugando en la calle en 2008; a la derecha, adolescentes en silencio mirando sus teléfonos en 2018.]*

"Buenos días, profesora, compañeros.
En análisis de datos hay una regla de oro: *'Si la audiencia no entiende el contexto, los datos no sirven de nada'*. Por eso, hoy no voy a empezar mostrándoles una tabla de Excel. Voy a empezar con una historia.

Imaginen el año 2010. La infancia estaba basada en el juego, en la exploración física, en aburrirse y crear. Pero entre 2010 y 2015, ocurrió lo que la literatura científica llama 'El Gran Recableado'. La infancia se volvió *phone-based*. Cambiamos las interacciones cara a cara por algoritmos. 

Mi proyecto nace de una pregunta de negocio y social muy clara: ¿Cuál es el coste real de esta transición digital en la salud mental de nuestros adolescentes? Y más importante aún... ¿Qué podemos hacer al respecto de forma medible?"

**(1:15 - 2:45) Cambio en el Tiempo: La Epidemia Silenciosa**
*[Diapositiva 2: Gráfico de línea simple y limpio. Eje Y: % de adolescentes tristes/desesperanzados. Eje X: Años (2005-2021). La línea sube constantemente.]*

"Para responder esto, utilicé dos bases de datos públicas de EE. UU., abarcando 16 años y más de 130 mil estudiantes.
Miremos primero cómo evolucionó la métrica a lo largo del tiempo.

En 2005, el 28% de los adolescentes reportaba sentirse 'triste o desesperanzado' por más de dos semanas seguidas. Para 2021, esa cifra saltó al 42%. 
*[Pausa dramática de 2 segundos]*
Un aumento del 48%. Pero en el análisis de datos, los promedios suelen ocultar la verdad. Como buenos analistas, debemos hacer un *Drill-down* y buscar los *Outliers*. ¿A quién está afectando realmente esta crisis?"

**(2:45 - 4:15) El Contraste: La Brecha de Género (El hallazgo más impactante)**
*[Diapositiva 3: Gráfico de barras comparativo. Dos líneas o barras que muestran cómo la brecha entre hombres y mujeres se ensancha drásticamente.]*

"Aquí es donde la historia se vuelve crítica. Miren este contraste.
Los chicos pasaron del 20% al 28%. Es un aumento, sí.
Pero las chicas... las chicas pasaron del 36% a casi el 57%. 

*[Señalar la brecha en el gráfico]*
La brecha de género se amplificó en un 71%. ¿Por qué? Los datos nos dan la hipótesis: las plataformas basadas en imágenes, como Instagram o TikTok, castigan desproporcionadamente a las mujeres mediante la comparación social constante. 

Y aquí va una lección clave del análisis: los datos deben empoderar a quien toma decisiones. Si un *stakeholder* me pregunta: *'¿Pero no están bajando las tasas de suicidio?'*, los datos me permiten darle una respuesta contundente."

**(4:15 - 5:30) Intersección y Paradoja: Depresión vs. Mortalidad**
*[Diapositiva 4: Gráfico de dispersión o doble eje. Muestra que a mayor depresión en mujeres, la mortalidad no sube proporcionalmente comparado con los hombres.]*

"Al cruzar los datos de encuestas con los de mortalidad, encontramos una paradoja.
Las mujeres tienen el doble de probabilidad de reportar depresión severa que los hombres, pero representan solo un tercio de la mortalidad por suicidio consumado. 

¿Qué nos dice esto como analistas? Que la mortalidad es un indicador rezagado y *no captura la carga real de salud mental*. Si los directivos solo miran las muertes, estamos ciegos ante el sufrimiento diario de millones de adolescentes. Necesitamos indicadores tempranos."

**(5:30 - 6:30) La Causa Raíz: La Curva en "J"**
*[Diapositiva 5: Gráfico de línea con forma de "J". Eje X: Horas de pantalla. Eje Y: Riesgo (Odds Ratio). El punto más bajo es 1 hora, se dispara a las 5 horas.]*

"Ahora, busquemos la causa raíz usando la técnica de *Factores*. ¿Es la tecnología el enemigo absoluto?
Los datos dicen que no. Al analizar las horas de pantalla, no encontramos una línea recta, sino una curva en forma de 'J'.

Usar una hora al día es, de hecho, el punto mínimo de riesgo. El problema, el verdadero detonante, comienza a partir de las 3 horas y se dispara a las 5 horas diarias, donde el riesgo de depresión se duplica.
No se trata de satanizar la pantalla, se trata de entender la dosis."

**(6:30 - 7:30) Rigor Metodológico**
*[Diapositiva 6: 3 Bullet points simples: "n=134,674 (Diseño Complejo)", "Pesos Muestrales y Cluster-Robust", "Control de Paradoja de Simpson".]*

"Ahora, hablemos de rigor — que en este tipo de análisis lo es todo. La regla es clara: *'Si no es confiable, no sirve'*.
Por eso, este análisis no es un simple cruce de variables en Python. Trabajé con el diseño muestral complejo del CDC. Apliqué regresiones logísticas ponderadas con errores estándar *cluster-robust* para corregir el efecto de diseño y evitar falsos positivos.
Además, validé que no estuviéramos cayendo en la Paradoja de Simpson al estratificar por raza y sexo. El patrón de la brecha de género es universal y estadísticamente blindado.
La evidencia es asociativa, sí, pero la señal es innegable."

**(7:30 - 8:45) La Solución: Phone-Free Schools (Escalable y Medible)**
*[Diapositiva 7: Tabla visual con las 4 palancas (Recoger, Reemplazar, Monitorear, Capacitar) y el ROI/KPIs.]*

"Un buen análisis no se queda en el diagnóstico. Hay que cerrar con soluciones escalables, y medibles.
Propongo el framework de ingeniería social: *Phone-Free Schools*. Cuatro palancas de acción:
1. **Recoger:** Lockers magnéticos (reducir la exposición).
2. **Reemplazar:** Recreo estructurado (llenar el vacío de atención).
3. **Monitorear:** Encuestas semestrales de bienestar.
4. **Capacitar:** Talleres para profesores.

¿El costo? 210 dólares por estudiante al año.
¿Cómo sabemos si funciona? Propongo evaluarlo mediante un ensayo controlado aleatorizado (RCT), con KPIs SMART claros: reducir la tristeza global al 33% en dos años. Es una solución basada estrictamente en datos."

**(8:45 - 9:15) Conclusión y Llamado a la Acción**
*[Diapositiva 8: Frase de cierre: "La data es el mapa. La decisión es nuestra." y tus datos de contacto.]*

"Para cerrar, vuelvo a la premisa inicial. Estos datos no son solo una colección de números sobre *teenagers* tristes. Son el mapa que nos permite rescatar a una generación que fue 'recableada' sin su consentimiento.
Tenemos el diagnóstico, tenemos la dosis de riesgo, y tenemos la solución. Ahora, como tomadores de decisiones, solo nos queda actuar.

Muchas gracias. Quedo a su entera disposición para cualquier pregunta."
