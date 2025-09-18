// Forfatter: Andreas Nordgaard aols0228
// Link til kilde: 
// 
// Beskrivelse: 
// I Tabular Editor 2-miljøet er de mest almindelige using-direktiver (såsom System, System.Linq og System.Collections.Generic) allerede tilgængelige.
// Så det er ikke nødvendigt at inkludere dem manuelt i scriptet.
// Bemærk at makroer fra TE3 skal omskrives til gammel C#-syntaks, da TE2 ikke understøtter C# 9.0 og nyere.
// 
// Changelog:
// ---------------------------------------------------------------
// Version | Dato DD-MM-YYYY | Forfatter | Beskrivelse
// 0.1.0     03-06-2025        aols0228    Klargøring af kode
// 1.0.0     25-06-2025        aols0228    Produktionsklar til dataenheden
// 1.1.0     18-09-2025        aols0228    Altid deploy til dap_sql_pbi_prod_fm1

string expressionName = "Cluster";

// Get target environment from environment variable (default: PROD)
var targetEnvironment = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT") ?? "PROD";

// Mapping: cluster name → warehouse path
var clusterToWarehouse = new Dictionary<string, string>();
clusterToWarehouse.Add("dap_sql_pbi_prod_fm1", "/sql/1.0/warehouses/fa8eae826752250f");
// Tilføj flere clusters her når de kommer
// clusterToWarehouse.Add("dap_sql_pbi_prod_all", "/sql/1.0/warehouses/xxxxx");

// Altid deploy til dap_sql_pbi_prod_fm1
string targetCluster = "dap_sql_pbi_prod_fm1";
string targetWarehousePath = clusterToWarehouse[targetCluster];

Info("targetEnvironment: " + targetEnvironment);

var expression = Model.Expressions[expressionName];

if (expression != null)
{
    // Opdater expression til target cluster
    expression.Expression = string.Format(
        "// Cluster - {0}\n" +
        "\"{1}\"\n" +
        "meta [\n" +
        "    IsParameterQuery = true,\n" +
        "    IsParameterQueryRequired = true,\n" +
        "    Type = type text\n" +
        "]",
        targetCluster,
        targetWarehousePath
    );
    
    Info("'" + expressionName + "' opdateret i " + targetEnvironment + " til: " + targetCluster + " " + targetWarehousePath);
}
else
{
    Info("Udtrykket '" + expressionName + "' blev ikke fundet.");
}