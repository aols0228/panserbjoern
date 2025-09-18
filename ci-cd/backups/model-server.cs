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
// 0.1.0     18-09-2025        aols0228    Klargøring af kode
// 1.0.0     18-09-2025        aols0228    Altid deploy til dap-analytiker-databricks

string expressionName = "Server";

// Get target environment from environment variable (default: PROD)
var targetEnvironment = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT") ?? "PROD";

// Mapping: server name → server address
var serverToAddress = new Dictionary<string, string>();
serverToAddress.Add("dap-analytiker-databricks", "adb-2776823572857644.4.azuredatabricks.net");
// Tilføj flere servers her når de kommer
// serverToAddress.Add("dap-analytiker-databricks-prod", "adb-xxxxx.x.azuredatabricks.net");

// Altid deploy til dap-analytiker-databricks
string targetServer = "dap-analytiker-databricks";
string targetServerAddress = serverToAddress[targetServer];

Info("targetEnvironment: " + targetEnvironment);

var expression = Model.Expressions[expressionName];

if (expression != null)
{
    // Opdater expression til target server
    expression.Expression = string.Format(
        "// Server - {0}\n" +
        "\"{1}\"\n" +
        "meta [\n" +
        "    IsParameterQuery = true,\n" +
        "    IsParameterQueryRequired = true,\n" +
        "    Type = type text\n" +
        "]",
        targetServer,
        targetServerAddress
    );
    
    Info("'" + expressionName + "' opdateret i " + targetEnvironment + " til: " + targetServer + " " + targetServerAddress);
}
else
{
    Info("Udtrykket '" + expressionName + "' blev ikke fundet.");
}