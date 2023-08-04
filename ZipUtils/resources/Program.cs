using System;
using System.IO.Compression;
using System.Text.Json;

public class Result
{
    public bool Success { get; set; }
    public string Path { get; set; }
}

public static class ZipFileUtility
{
    public static Result DeleteFileFromZip(string zipFilePath, string fileToDelete)
    {
        var result = new Result
        {
            Path = fileToDelete
        };

        try
        {
            using (ZipArchive archive = ZipFile.Open(zipFilePath, ZipArchiveMode.Update))
            {
                ZipArchiveEntry entryToDelete = archive.GetEntry(fileToDelete);
                if (entryToDelete != null)
                {
                    entryToDelete.Delete();
                    result.Success = true;
                }
                else
                {
                    result.Success = false;
                }
            }
        }
        catch (Exception)
        {
            result.Success = false;
        }

        return result;
    }
}

class Program
{
    // Define a model to represent the input data
    public class InputModel
    {
        public string ZipFilePath { get; set; }
        public string FileToDelete { get; set; }
    }

    static void Main()
    {
        string jsonString = Console.In.ReadToEnd();
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        // Parse the JSON input
        try
        {
            var inputObject = JsonSerializer.Deserialize<InputModel>(jsonString, options);
            if (inputObject != null)
            {
                // Call the DeleteFileFromZip function with the parsed inputs
                var result = ZipFileUtility.DeleteFileFromZip(inputObject.ZipFilePath, inputObject.FileToDelete);
                
                var jsonResult = JsonSerializer.Serialize(result);
                Console.WriteLine(jsonResult);
            }
            else
            {
                Console.WriteLine("{\"Success\": false, \"Path\": \"Invalid input format.\"}");
            }
        }
        catch (JsonException)
        {
            Console.WriteLine("{\"Success\": false, \"Path\": \"Invalid JSON format.\"}");
        }
    }
}
