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

string expressionName = "Cluster";

// Get target environment from environment variable (default: PROD)
var targetEnvironment = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT") ?? "PROD";

// Mapping: cluster name → warehouse path
var clusterToWarehouse = new Dictionary<string, string>();
clusterToWarehouse.Add("dap_sql_fm1", "/sql/1.0/warehouses/cee95f8c2cee3043");
clusterToWarehouse.Add("dap_sql_fm2", "/sql/1.0/warehouses/eee4c6d8c239baa6");
clusterToWarehouse.Add("dap_sql_fm3", "/sql/1.0/warehouses/9a7f5066c07f5bb1");
clusterToWarehouse.Add("dap_sql_pbi_prod_fm1", "/sql/1.0/warehouses/fa8eae826752250f");
// Nedenstående konverteringer er for at skabe en blød konvertering for eksisterende modeller fra sandbox-miljøet til dtp-miljøet
clusterToWarehouse.Add("dap_sql_fm1_sandbox", "/sql/1.0/warehouses/cf47b55950f39277");
clusterToWarehouse.Add("dap_sql_fm2_sandbox", "/sql/1.0/warehouses/93e1e1aeb64248bc");
clusterToWarehouse.Add("dap_sql_fm3_sandbox", "/sql/1.0/warehouses/52ccf0707877c870");
clusterToWarehouse.Add("dap_sql_pbi_prod_fm1_sandbox", "/sql/1.0/warehouses/986377cfde3bfec7");
clusterToWarehouse.Add("dap_sql_pbi_prod_fm2_sandbox", "/sql/1.0/warehouses/7770ec42b0b41d04");
clusterToWarehouse.Add("dap_sql_pbi_prod_fm3_sandbox", "/sql/1.0/warehouses/2de1f7039afc1652");

// Mapping: dev cluster name → prod cluster name
var devToProdCluster = new Dictionary<string, string>();
devToProdCluster.Add("dap_sql_fm1", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_fm2", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_fm3", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_fm1_sandbox", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_fm2_sandbox", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_fm3_sandbox", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_prod_fm1_sandbox", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_prod_fm2_sandbox", "dap_sql_prod_fm1");
devToProdCluster.Add("dap_sql_prod_fm3_sandbox", "dap_sql_prod_fm1");

Info("targetEnvironment: " + targetEnvironment);

var expression = Model.Expressions.FirstOrDefault(e => e.Name == expressionName);

if (expression != null)
{
    // Split expression into lines
    var lines = expression.Expression.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);

    // Find linjen med en kendt warehouse-sti
    string currentWarehousePath = clusterToWarehouse.Values
        .FirstOrDefault(path => lines.Any(line => line.Contains(path)));

    if (currentWarehousePath != null)
    {
        // Find dev cluster ud fra warehouse-stien
        string devCluster = clusterToWarehouse
            .FirstOrDefault(kv => currentWarehousePath.Contains(kv.Value)).Key;

        if (string.IsNullOrEmpty(devCluster))
        {
            throw new InvalidOperationException(
                string.Format("Ukendt warehouse-sti: '{0}'.\nIndstil {1}-værdien og kør makro igen.", currentWarehousePath, expressionName));
        }

        // Map dev cluster til prod cluster hvis muligt
        string targetCluster = devToProdCluster.ContainsKey(devCluster)
            ? devToProdCluster[devCluster]
            : devCluster;

        // Find ny warehouse-sti
        string newWarehousePath = clusterToWarehouse[targetCluster];

        // Brug string.Format til at opdatere expression
        expression.Expression = string.Format(
            "// Cluster - {0}\n" +
            "\"{1}\"\n" +
            "meta [\n" +
            "    IsParameterQuery = true,\n" +
            "    IsParameterQueryRequired = true,\n" +
            "    Type = type text\n" +
            "]",
            targetCluster,
            newWarehousePath
        );
        // Info("Udtrykket '" + expressionName + "' er blevet opdateret til: " + targetCluster);
        Info("'" + expressionName + "' opdateret i " + targetEnvironment + " til: " + targetCluster + " " + newWarehousePath);
    }
    else
    {
        Info("Ingen kendt warehouse-sti fundet i udtrykket '" + expressionName + "'.");
    }
}
else
{
    Info("Udtrykket '" + expressionName + "' blev ikke fundet.");
}