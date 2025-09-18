// Forfatter: Andreas Nordgaard aols0228
// Link til kilde: 
// 
// Beskrivelse:
// Makro, der ændrer Catalog til produktion ved at fjerne _sandbox
// Bemærk at makroer fra TE3 skal omskrives til gammel C#-syntaks, da TE2 ikke understøtter C# 9.0 og nyere.
// 
// Changelog:
// ---------------------------------------------------------------
// Version | Dato DD-MM-YYYY | Forfatter | Beskrivelse
// 0.1.0     03-06-2025        aols0228    Klargøring af kode
// 1.0.0     25-06-2025        aols0228    Produktionsklar til dataenheden
// 1.0.1     21-08-2025        aols0228    Refaktoreret til TabularEditor script - fjernet Program/Main klasser
// 1.1.0     16-09-2025        Converted   Konverteret til TE3 TOM og tilføjet dap*_[dt funktionalitet

using System;
using System.Text.RegularExpressions;
using System.Collections.Generic;

public class ExpressionInfo
{
    public string Key { get; set; }
    public string Value { get; set; }
    public string Description { get; set; }
}

public class Program
{
    public static void Main()
    {
        // Define the key, Environment suffix, and description dictionary for Produktion and Udvikling
        var key = "Catalog";
        var Environment = "_sandbox";
        var DescriptionDictionary = new Dictionary<bool, string>
        {
            { true, "Produktion" },
            { false, "Udvikling" }
        };

        // Define whether we are shifting to Produktion (true) or Udvikling (false)
        bool ShiftEnvironment = true; // True shifts to Produktion and removes Environment; False shifts to Udvikling and adds Environment

        // Create the expression info and set the key and initial value
        var Expression = new ExpressionInfo
        {
            Key = key,
            Value = Model.Expressions[key].Expression
        };

        // Step 1: Remove both single-line and multi-line comments
        var commentPattern = @"//.*?$|/\*.*?\*/";
        var withoutComments = Regex.Replace(Expression.Value, commentPattern, string.Empty, RegexOptions.Singleline | RegexOptions.Multiline);

        // Step 2: Capture the first quoted substring not in comment section
        Regex regex = new Regex("\"([^\"]*)\"");
        var match = regex.Match(withoutComments);

        if (match.Success)
        {
            var extractedValue = match.Groups[1].Value;

            if (string.IsNullOrWhiteSpace(extractedValue))
            {
                throw new InvalidOperationException("Indstil " + key + "-værdien og kør makro igen");
            }

    // Transform the value
            extractedValue = ShiftEnvironment
                ? (extractedValue.EndsWith(Environment)
                    ? extractedValue.Substring(0, extractedValue.Length - Environment.Length)
                    : extractedValue)
                : (extractedValue.EndsWith(Environment)
                    ? extractedValue
                    : extractedValue + Environment);

            Expression.lineDescription = key + " - " + DescriptionDictionary[ShiftEnvironment];

            Model.Expressions[Expression.Key].Expression =
                "// " + Expression.lineDescription + "\n" +
                "\"" + extractedValue + "\"\n" +
                "meta [\n" +
                "    IsParameterQuery         = true,\n" +
                "    IsParameterQueryRequired = true,\n" +
                "    Type                     = type text\n" +
                "]";
            // Info("Udtrykket '" + Expression.Key + "' er blevet opdateret til: " + extractedValue);
            Info("'" + Expression.Key + "' opdateret i produktion til: " + extractedValue);
        }
        else
        {
            Info("No quoted string found in the expression.");
        }
    }
}
