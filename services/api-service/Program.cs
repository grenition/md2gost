using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using Md2Gost.Api;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.Services.AddHttpClient<ConverterService>(client =>
{
    var docxServiceUrl = builder.Configuration["DocxService:Url"] ?? "http://docx-service:5000";
    if (!docxServiceUrl.EndsWith("/"))
    {
        docxServiceUrl += "/";
    }
    client.BaseAddress = new Uri(docxServiceUrl);
    client.Timeout = TimeSpan.FromMinutes(5);
});

builder.Services.AddScoped<ConverterService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseCors();
app.UseRouting();
app.MapControllers();

app.Run();

