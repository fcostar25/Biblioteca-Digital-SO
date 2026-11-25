/*
 * Código real del proyecto (src/biblioteca_basica.py y src/biblioteca_compleja.py),
 * método prestar() de cada clase, con sus números de línea originales.
 * Generado automáticamente: si cambias el código en src/, actualiza también este archivo.
 */
const CODIGO = {
 "sin": {
  "basica": {
   "inicio": 73,
   "lineas": [
    "    def prestar(self, usuario, titulo):",
    "        if not self._es_mi_libro(usuario, titulo):",
    "            return False",
    "",
    "        # ============ INICIO SECCIÓN CRÍTICA ============",
    "        disponibles = self.copias_disponibles                    # 1. CONSULTA",
    "        self.log(f\"{usuario} consulta: {disponibles} copia(s) disponible(s)\")",
    "",
    "        if disponibles > 0:                                      # 2. VALIDACIÓN",
    "            time.sleep(DEMORA)  # procesando... otro hilo puede entrar aquí",
    "            self.copias_disponibles -= 1                         # 3. ACTUALIZACIÓN",
    "            prestado = True",
    "        else:",
    "            prestado = False",
    "        # ============= FIN SECCIÓN CRÍTICA ==============",
    "",
    "        if prestado:",
    "            self.log(f\"{usuario} recibe el libro -> quedan {self.copias_disponibles}\")",
    "        else:",
    "            self.log(f\"{usuario}: solicitud rechazada, no hay copias\")",
    "        return prestado"
   ]
  },
  "compleja": {
   "inicio": 92,
   "lineas": [
    "    def prestar(self, usuario, titulo):",
    "        if not self._existe(usuario, titulo):",
    "            return False",
    "",
    "        # ============ INICIO SECCIÓN CRÍTICA ============",
    "        libro = self.inventario[titulo]",
    "        disponibles = libro[\"disponibles\"]                       # 1. CONSULTA",
    "        self.log(f\"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)\")",
    "",
    "        if disponibles > 0:                                      # 2. VALIDACIÓN",
    "            time.sleep(DEMORA)  # procesando... otro hilo puede entrar aquí",
    "            libro[\"disponibles\"] -= 1                            # 3. ACTUALIZACIÓN",
    "            self._registrar(usuario, titulo, \"préstamo\")         # 4. REGISTRO",
    "            prestado = True",
    "        else:",
    "            prestado = False",
    "        # ============= FIN SECCIÓN CRÍTICA ==============",
    "",
    "        if prestado:",
    "            self.log(f\"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}\")",
    "        else:",
    "            self.log(f\"{usuario}: préstamo de '{titulo}' rechazado, no hay copias\")",
    "        return prestado"
   ]
  }
 },
 "mutex": {
  "basica": {
   "inicio": 127,
   "lineas": [
    "    def prestar(self, usuario, titulo):",
    "        if not self._es_mi_libro(usuario, titulo):",
    "            return False",
    "",
    "        self.log(f\"{usuario} pide el libro y espera el mutex\")",
    "",
    "        # >>> ADQUIERE el mutex: si otro hilo lo tiene, este hilo se bloquea aquí.",
    "        with self.lock:",
    "            self.log(f\"{usuario} [LOCK] entra a la sección crítica\")",
    "",
    "            # ============ INICIO SECCIÓN CRÍTICA ============",
    "            disponibles = self.copias_disponibles                # 1. CONSULTA",
    "            self.log(f\"{usuario} consulta: {disponibles} copia(s) disponible(s)\")",
    "",
    "            if disponibles > 0:                                  # 2. VALIDACIÓN",
    "                time.sleep(DEMORA)  # procesando... los demás esperan",
    "                self.copias_disponibles -= 1                     # 3. ACTUALIZACIÓN",
    "                prestado = True",
    "            else:",
    "                prestado = False",
    "            # ============= FIN SECCIÓN CRÍTICA ==============",
    "",
    "            if prestado:",
    "                self.log(f\"{usuario} recibe el libro -> quedan {self.copias_disponibles}\")",
    "            else:",
    "                self.log(f\"{usuario}: solicitud rechazada, no hay copias\")",
    "            self.log(f\"{usuario} [UNLOCK] sale de la sección crítica\")",
    "        # <<< LIBERA el mutex al salir del with (también si ocurre una excepción).",
    "",
    "        return prestado"
   ]
  },
  "compleja": {
   "inicio": 158,
   "lineas": [
    "    def prestar(self, usuario, titulo):",
    "        if not self._existe(usuario, titulo):",
    "            return False",
    "",
    "        self.log(f\"{usuario} pide '{titulo}' y espera el mutex\")",
    "",
    "        # >>> ADQUIERE el mutex: si otro hilo lo tiene, este hilo se bloquea aquí.",
    "        with self.lock:",
    "            self.log(f\"{usuario} [LOCK] entra a la sección crítica\")",
    "",
    "            # ============ INICIO SECCIÓN CRÍTICA ============",
    "            libro = self.inventario[titulo]",
    "            disponibles = libro[\"disponibles\"]                   # 1. CONSULTA",
    "            self.log(f\"{usuario} consulta '{titulo}': {disponibles} copia(s) disponible(s)\")",
    "",
    "            if disponibles > 0:                                  # 2. VALIDACIÓN",
    "                time.sleep(DEMORA)  # procesando... los demás esperan",
    "                libro[\"disponibles\"] -= 1                        # 3. ACTUALIZACIÓN",
    "                self._registrar(usuario, titulo, \"préstamo\")     # 4. REGISTRO",
    "                prestado = True",
    "            else:",
    "                prestado = False",
    "            # ============= FIN SECCIÓN CRÍTICA ==============",
    "",
    "            if prestado:",
    "                self.log(f\"{usuario} recibe '{titulo}' -> quedan {libro['disponibles']}\")",
    "            else:",
    "                self.log(f\"{usuario}: préstamo de '{titulo}' rechazado, no hay copias\")",
    "            self.log(f\"{usuario} [UNLOCK] sale de la sección crítica\")",
    "        # <<< LIBERA el mutex al salir del with (también si ocurre una excepción).",
    "",
    "        return prestado"
   ]
  }
 }
};
