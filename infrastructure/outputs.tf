output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "search_service_name" {
  value = azurerm_search_service.search.name
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.cosmos.endpoint
}

output "postgresql_fqdn" {
  value = azurerm_postgresql_flexible_server.pg.fqdn
}

# Azure Cognitive Services (OpenAI)
output "openai_account_name" {
  value = azurerm_cognitive_account.openai.name
}
