using System.Net;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => new {msg = "Olá, Kubernetes C#", POD = Dns.GetHostName()});
app.Run();