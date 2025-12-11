using System.Text;
using System.Text.Json;

namespace Md2Gost.Api;

public class ConverterService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ConverterService> _logger;

    public ConverterService(HttpClient httpClient, ILogger<ConverterService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<byte[]> ConvertToDocxAsync(string markdown, bool syntaxHighlighting, string? sessionId = null)
    {
        var request = new
        {
            markdown = markdown,
            syntax_highlighting = syntaxHighlighting,
            session_id = sessionId
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var baseUrl = _httpClient.BaseAddress ?? new Uri("http://docx-service:5000/");
        var requestUri = new Uri(baseUrl, "api/convert");
        var response = await _httpClient.PostAsync(requestUri, content);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadAsByteArrayAsync();
    }

    public async Task<string> ConvertToPreviewAsync(string markdown, bool syntaxHighlighting, string? sessionId = null)
    {
        var request = new
        {
            markdown = markdown,
            syntax_highlighting = syntaxHighlighting,
            session_id = sessionId
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var baseUrl = _httpClient.BaseAddress ?? new Uri("http://docx-service:5000/");
        var requestUri = new Uri(baseUrl, "api/preview");
        var response = await _httpClient.PostAsync(requestUri, content);
        response.EnsureSuccessStatusCode();

        var responseContent = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<PreviewResponse>(responseContent, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });

        return result?.Pdf ?? string.Empty;
    }
}

public class PreviewResponse
{
    public string Pdf { get; set; } = string.Empty;
}

