terraform {
  required_version = ">= 1.2.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.80.0"
    }
  }
}

provider "azurerm" {
  features {}
}

#————————————————————————————
# Resource Group
#————————————————————————————
resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
}

#————————————————————————————
# Azure Cognitive Search (Free Tier)
#————————————————————————————
resource "azurerm_search_service" "search" {
  name                = "${var.prefix}-search"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "free"
  partition_count     = 1
  replica_count       = 1
}

#————————————————————————————
# Azure Cosmos DB (Free Tier; enable vector search manually)
#————————————————————————————
resource "azurerm_cosmosdb_account" "cosmos" {
  name                = "${var.prefix}-cosmos"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  # Azure free tier (400 RU/s included)
  free_tier_enabled = true

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }
}

#————————————————————————————
# PostgreSQL Flexible Server (smallest burstable SKU)
#————————————————————————————
resource "azurerm_postgresql_flexible_server" "pg" {
  name                = "${var.prefix}-pg"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location

  administrator_login    = var.pg_admin_username
  administrator_password = var.pg_admin_password

  version    = "15"
  sku_name   = "B_Standard_B1ms"   # smallest burstable tier :contentReference[oaicite:3]{index=3}
  storage_mb = 32768               # minimum allowed (32 GB)

  backup_retention_days        = 7
  public_network_access_enabled = true
}

resource "azurerm_postgresql_flexible_server_database" "main_db" {
  name      = "ragdb"
  server_id = azurerm_postgresql_flexible_server.pg.id
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_all" {
  name             = "allow_all"
  server_id        = azurerm_postgresql_flexible_server.pg.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

#————————————————————————————
# Azure OpenAI via Cognitive Services Account
#————————————————————————————
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.prefix}-openai"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location

  kind     = "OpenAI"
  sku_name = "S0"
}
