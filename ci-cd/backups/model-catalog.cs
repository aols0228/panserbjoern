// Forfatter: Andreas Nordgaard aols0228
// Link til kilde: 
// 
// Beskrivelse:
// Makro, der sætter Catalog expression til databricks_catalog_name fra environment variable
// 
// Changelog:
// ---------------------------------------------------------------
// Version | Dato DD-MM-YYYY | Forfatter | Beskrivelse
// 0.1.0     03-06-2025        aols0228    Klargøring af kode
// 1.0.0     25-06-2025        aols0228    Produktionsklar til dataenheden
// 1.0.1     21-08-2025        aols0228    Refaktoreret til TabularEditor script - fjernet Program/Main klasser
// 1.1.0     16-09-2025        Converted   Konverteret til TE3 TOM og tilføjet dap*_[dt funktionalitet
// 1.2.0     16-09-2025        aols0228    Cleaned up version - fjernet kompleksitet
// 1.2.1     16-09-2025        aols0228    Konverteret til Tabular Editor 2 format
// 1.3.0     16-09-2025        aols0228    Simplified - bruger databricks_catalog_name direkte

var key = "Catalog";

// Get parameters from environment variables
var databricksCatalogName = Environment.GetEnvironmentVariable("databricks_catalog_name");
var targetEnvironment = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT") ?? "PROD"; // Default: PROD

if (string.IsNullOrWhiteSpace(databricksCatalogName))
{
    throw new InvalidOperationException("Environment variable 'databricks_catalog_name' is not set or empty");
}

Info("databricks_catalog_name: " + databricksCatalogName);
Info("targetEnvironment: " + targetEnvironment);

// Check if the expression exists and get it
var expression = Model.Expressions[key];
if (expression == null)
{
    throw new InvalidOperationException("Expression '" + key + "' not found in the model.");
}

// Update the expression with the databricks catalog name
expression.Expression =
    "// " + key + " - " + targetEnvironment + "\n" +
    "\"" + databricksCatalogName + "\"\n" +
    "meta [\n" +
    "    IsParameterQuery         = true,\n" +
    "    IsParameterQueryRequired = true,\n" +
    "    Type                     = type text\n" +
    "]";

Info("'" + key + "' opdateret til: " + databricksCatalogName);