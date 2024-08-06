provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "asp" {
  name                = "${var.function_app_name}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "FunctionApp"
  reserved            = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_function_app" "function" {
  name                       = var.function_app_name
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  app_service_plan_id        = azurerm_app_service_plan.asp.id
  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key
  os_type                    = "linux"

  site_config {
    linux_fx_version = "DOCKER|${var.acr_name}.azurecr.io/clickstream_generator:${var.acr_image_tag}"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME             = "python"
    PYTHON_VERSION                       = "3.11"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE  = "false"
    AzureWebJobsStorage                  = azurerm_storage_account.storage.primary_connection_string
  }

  version = "~4"
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "location" {
  description = "The location of the resource group"
  type        = string
  default     = "francecentral"
}

variable "function_app_name" {
  description = "The name of the Function App"
  type        = string
}

variable "storage_account_name" {
  description = "The name of the Storage Account"
  type        = string
}

variable "acr_name" {
  description = "The name of the Azure Container Registry"
  type        = string
}

variable "acr_image_tag" {
  description = "The Docker image tag for the Azure Container Registry"
  type        = string
  default     = "latest"
}
