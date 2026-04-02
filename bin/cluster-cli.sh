#!/bin/bash

# Select Malomo Cluster
ml() {
  env="$(select_env $1)"
  tsh kube login "$env"
}

banner() {
  if [ $1 == 'production' ]; then
    color='212'
  else
    color='180'
  fi

  gum style \
    --foreground "$color" --border-foreground "$color" --border double \
    --align center --width 50 --margin "1 1" --padding "2 4" \
    "Connected to $1"
}

env_banner() {
  clusters=$(tsh kube ls -f json)
  cluster=$(echo $clusters | jq -r '.[] | select(.selected == true) | .kube_cluster_name')
  banner $cluster
}

select_env() {
  if [[ ! -z "$1" ]]; then
    echo "$1"
    return
  fi
  echo 'production staging' | tr ' ' '\n' | gum filter --placeholder 'Select environment:'
}

select_app() {
  if [[ ! -z "$1" ]]; then
    echo "$1"
    return
  fi
  apps=$(echo "core integration-klaviyo integration-attentive integration-shopify integration-postscript integration-loop" | tr ' ' '\n')
  echo $apps | gum filter --placeholder "Select application:"
}


get_running_pods() {
  kubectl get pods -n $1 -o json | jq -r '.items[] | select(.status.phase == "Running") | .metadata.name'
}

# Shell into Malomo Deployment
msh() {
  env_banner
  app="$(select_app $1)"
  kubectl exec -n "$app" deployments/$app -it -- sh
}

# prompts to select a specific pod
mshp() {
  env_banner
  app="$(select_app $1)"
  running_pods=$(get_running_pods $app)
  pod=$(echo $running_pods | gum filter --placeholder "Select pod:" | awk '{ print $1 }')
  gum style --foreground 50 --margin "1 1" "Selected pod: $pod"
  kubectl exec $pod -it -n $app -- sh
}

# shell into iex for an app
miex() {
  env_banner
  app="$(select_app $1)"
  bin_name=$(echo "$app" | tr '-' '_')
  kubectl exec -n "$app" deployments/$app -it -- "$bin_name" 'remote'
}

# show logs for a deployment
mlog() {
  env_banner
  app="$(select_app $1)"
  kubectl logs -f -l "app=$app" -n $app
}

# show logs for a pod
mlogp() {
  env_banner
  app="$(select_app $1)"
  running_pods=$(get_running_pods $app)
  pod=$(echo $running_pods | gum filter --placeholder "Select pod:" | awk '{ print $1 }')
  gum style --foreground 50 --margin "1 1" "Selected pod: $pod"
  kubectl logs -f $pod -n $app
}

select_pod() {
  running_pods=$(get_running_pods $app)
  pod=$(echo $running_pods | gum filter --placeholder "Select pod:" | awk '{ print $1 }')
  echo "$pod"
}

select_port() {
  if [[ ! -z "$1" ]]; then
    echo "$1"
    return
  fi

  port="$(gum input --placeholder '31234' --char-limit=5)"
  echo "$port"
}

# port forward to postgres
mpfpg() {
  env_banner
  app="$(select_app $1)"
  pod="$(select_pod)"
  local_port="$(select_port $2)"
  kubectl port-forward -n "$app" "$pod" "$local_port:5432"
}

# alert when a deploy is done
watchrun() {
  app=$(basename="$(basename "$(pwd)")" && [[ $basename =~ "-" ]] && echo "$basename" | tr '-' ' ' | awk '{print $2}' || echo "$basename")
  gh run watch --exit-status && say "$app DEPLOY DONE" && unicornleap -n 5 && (figlet 'DEPLOYED' | lolcat) || ((figlet 'OH NO, FAILED!' | lolcat) && say "OH NO! $app deployment failed" && unicornleap -u ~/Pictures/sad.png -k ~/Pictures/tear.png -n 5)
}

# psql into master
mmpsql() {
  pod=$(kubectl get pod -n core -l 'role=primary' -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -it -n core "$pod" -- psql 'core' "$@"
}

# psql into replica
mrpsql() {
  pod=$(kubectl get pod -n core -l 'role=replica' -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -it -n core "$pod" -- psql 'core' "$@"
}
