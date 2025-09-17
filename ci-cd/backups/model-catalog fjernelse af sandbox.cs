// Forfatter: Andreas Nordgaard aols0228
// Link til kilde: 
// 
// Beskrivelse:
// Makro, der ændrer Catalog til produktion ved at fjerne _sandbox
// Tilføjet funktionalitet til at lede efter "dap*_[dt" og udskifte med "dap_p"
// Konverteret til Tabular Editor 3 med TOM (Tabular Object Model)
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

var key = "Catalog";
var removeOptionalSuffix = "_sandbox"; // Define suffix as variable

// Get parameters from environment variables (with defaults)
var targetEnvironment = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT") ?? "PROD";
var targetEnvironmentPrefix = Environment.GetEnvironmentVariable("TARGET_ENVIRONMENT_PREFIX") ?? "p";

Info("var targetEnvironment: " + targetEnvironment);
Info("var targetEnvironmentPrefix: " + targetEnvironmentPrefix);

// Check if the expression exists and get it
var expression = Model.Expressions[key];
if (expression == null)
{
    throw new InvalidOperationException("Expression '" + key + "' not found in the model.");
}

// Remove comments
var withoutComments = Regex.Replace(expression.Expression, @"//.*?$|/\*.*?\*/", 
    string.Empty, RegexOptions.Singleline | RegexOptions.Multiline);

// Extract first quoted string
var match = Regex.Match(withoutComments, "\"([^\"]*)\"");

if (!match.Success)
{
    Info("No quoted string found in the expression.");
    return;
}

var extractedValue = match.Groups[1].Value;

if (string.IsNullOrWhiteSpace(extractedValue))
{
    throw new InvalidOperationException("Indstil " + key + "-værdien og kør makro igen");
}

// Convert dap_d or dap_t to target prefix at start of string
var originalMatch = Regex.Match(extractedValue, @"^dap_[dt]");
if (originalMatch.Success)
{
    var originalPrefix = originalMatch.Value; // Capture what was matched (dap_d or dap_t)
    extractedValue = Regex.Replace(extractedValue, @"^dap_[dt]", targetEnvironmentPrefix);
    Info("Konverteret " + originalPrefix + " mønster til " + targetEnvironmentPrefix);
}

// Remove _sandbox if present (case-insensitive)
if (extractedValue.EndsWith(removeOptionalSuffix, StringComparison.OrdinalIgnoreCase))
{
    extractedValue = extractedValue.Substring(0, extractedValue.Length - removeOptionalSuffix.Length);
    Info("Fjernet " + removeOptionalSuffix + " suffiks");
}

// Update the expression
expression.Expression =
    "// " + key + " - " + targetEnvironment + "\n" +
    "\"" + extractedValue + "\"\n" +
    "meta [\n" +
    "    IsParameterQuery         = true,\n" +
    "    IsParameterQueryRequired = true,\n" +
    "    Type                     = type text\n" +
    "]";

Info("'" + key + "' opdateret til: " + extractedValue);