using Microsoft.AspNetCore.Mvc;
using System.Text;
using System.Text.Json;

namespace Md2Gost.Api.Controllers;

[ApiController]
[Route("api")]
public class ConverterController : ControllerBase
{
    private readonly ConverterService _converterService;
    private readonly ILogger<ConverterController> _logger;

    public ConverterController(ConverterService converterService, ILogger<ConverterController> logger)
    {
        _converterService = converterService;
        _logger = logger;
    }

    [HttpPost("convert")]
    public async Task<IActionResult> Convert([FromBody] ConvertRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Markdown))
            {
                return BadRequest(new { error = "Markdown content is required" });
            }

            var docxBytes = await _converterService.ConvertToDocxAsync(
                request.Markdown,
                request.SyntaxHighlighting ?? true
            );

            return File(docxBytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "document.docx");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error converting markdown to DOCX");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("preview")]
    public async Task<IActionResult> Preview([FromBody] PreviewRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Markdown))
            {
                return BadRequest(new { error = "Markdown content is required" });
            }

            var pdf = await _converterService.ConvertToPreviewAsync(
                request.Markdown,
                request.SyntaxHighlighting ?? true
            );

            return Ok(new { pdf });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating preview");
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpGet("health")]
    public IActionResult Health()
    {
        return Ok(new { status = "healthy", service = "api-service" });
    }
}

public class ConvertRequest
{
    public string Markdown { get; set; } = string.Empty;
    public bool? SyntaxHighlighting { get; set; }
}

public class PreviewRequest
{
    public string Markdown { get; set; } = string.Empty;
    public bool? SyntaxHighlighting { get; set; }
}

