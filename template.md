# Plantilla de Análisis de Registros

Los registros tienen el siguiente formato:

| Account ID | Amount (USD) | Country        | Status |
|------------|--------------|----------------|--------|
| 1001       | 1,250.75     | United States  | OK     |
| 1002       | -420.10      | Italy          | KO     |
| 1003       | 3,900.00     | Canada         | OK     |
| 1004       | -1,875.60    | Australia      | KO     |
| 1005       | 2,210.25     | Spain          | OK     |
| 1006       | 5,420.80     | United Arab Emirates | OK     |
| 1007       | -750.40      | Mexico         | KO     |
| 1008       | 4,300.00     | Germany        | OK     |
| 1009       | -1,640.95    | Brazil         | KO     |
| 1010       | 7,520.55     | France         | OK     |

Los campos son:
 - Account ID: Identificador único de cliente.
 - Amount: Cantidad transferida. Si es positiva, representa un ingreso; si es negativa, representa un desembolso.
 - Country: País de la cuenta, correlacionado con ella de forma que cada cuenta solo tiene un país.
 - Status: OK representa que la transacción se ha realizado, KO representa que se ha rechazado.

Necesitamos analizarlos con los siguientes criterios:
 - Genera un fichero nuevo, con los logs limpios, es decir, manteniendo sólo los que tienen Status=OK.
 - Utiliando este fichero limpio, genera un fichero .csv que contenga dos columnas: Account ID y la suma de sus transacciones.