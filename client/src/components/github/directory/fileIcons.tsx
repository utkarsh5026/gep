import {
  DiJavascript1,
  DiCss3,
  DiHtml5,
  DiReact,
  DiPython,
  DiSass,
  DiLess,
  DiJava,
  DiRuby,
  DiPhp,
  DiSwift,
  DiGo,
  DiRust,
} from "react-icons/di";

import {
  SiTypescript,
  SiJson,
  SiMarkdown,
  SiGit,
  SiDocker,
  SiCplusplus,
  SiC,
  SiLua,
  SiKotlin,
  SiDart,
  SiScala,
  SiGradle,
  SiYaml,
  SiRedux,
  SiGraphql,
  SiPostgresql,
  SiVuedotjs,
  SiAngular,
  SiSvelte,
  SiTailwindcss,
  SiPrisma,
  SiNextdotjs,
  SiNuxtdotjs,
  SiElectron,
  SiNodedotjs,
  SiYarn,
  SiShell,
  SiXml,
} from "react-icons/si";

import {
  VscFile,
  VscFolder,
  VscFolderLibrary,
  VscSourceControl,
  VscBeaker,
  VscProject,
  VscSymbolNamespace,
  VscFileMedia,
  VscTools,
  VscSettingsGear,
  VscJson,
  VscPackage,
  VscGithub,
} from "react-icons/vsc";
import { IconType } from "react-icons";

interface FileIconConfig {
  icon: IconType;
  color: string;
}

interface FileIconMapping {
  [key: string]: FileIconConfig;
}

interface DirectoryIconMapping {
  [key: string]: FileIconConfig;
}

export const fileIcons: FileIconMapping = {
  // JavaScript & TypeScript
  js: { icon: DiJavascript1, color: "text-yellow-600 dark:text-yellow-400" },
  jsx: { icon: DiReact, color: "text-blue-600 dark:text-blue-400" },
  ts: { icon: SiTypescript, color: "text-blue-700 dark:text-blue-600" },
  tsx: { icon: SiTypescript, color: "text-blue-700 dark:text-blue-600" },

  // Web Markup & Styling
  html: { icon: DiHtml5, color: "text-orange-600 dark:text-orange-500" },
  css: { icon: DiCss3, color: "text-blue-600 dark:text-blue-500" },
  scss: { icon: DiSass, color: "text-pink-600 dark:text-pink-500" },
  sass: { icon: DiSass, color: "text-pink-600 dark:text-pink-500" },
  less: { icon: DiLess, color: "text-blue-500 dark:text-blue-400" },

  // Configuration Files
  json: { icon: SiJson, color: "text-yellow-700 dark:text-yellow-600" },
  yaml: { icon: SiYaml, color: "text-red-600 dark:text-red-500" },
  yml: { icon: SiYaml, color: "text-red-600 dark:text-red-500" },
  toml: { icon: VscFile, color: "text-gray-600 dark:text-gray-500" },
  xml: { icon: SiXml, color: "text-orange-700 dark:text-orange-600" },
  env: { icon: VscFile, color: "text-green-700 dark:text-green-600" },
  "env.local": { icon: VscFile, color: "text-green-600" },
  "env.development": { icon: VscFile, color: "text-green-600" },
  "env.production": { icon: VscFile, color: "text-green-600" },

  // Documentation
  md: { icon: SiMarkdown, color: "text-gray-600" },
  mdx: { icon: SiMarkdown, color: "text-gray-600" },

  // Programming Languages
  py: { icon: DiPython, color: "text-blue-500" },
  java: { icon: DiJava, color: "text-red-500" },
  rb: { icon: DiRuby, color: "text-red-600" },
  php: { icon: DiPhp, color: "text-purple-500" },
  swift: { icon: DiSwift, color: "text-orange-500" },
  go: { icon: DiGo, color: "text-blue-500" },
  rs: { icon: DiRust, color: "text-orange-600" },
  cpp: { icon: SiCplusplus, color: "text-blue-600" },
  c: { icon: SiC, color: "text-blue-500" },
  lua: { icon: SiLua, color: "text-blue-700" },
  kt: { icon: SiKotlin, color: "text-orange-500" },
  dart: { icon: SiDart, color: "text-blue-500" },
  scala: { icon: SiScala, color: "text-red-500" },

  // Framework-specific
  vue: { icon: SiVuedotjs, color: "text-green-600 dark:text-green-500" },
  svelte: { icon: SiSvelte, color: "text-orange-600" },
  angular: { icon: SiAngular, color: "text-red-600" },
  sh: { icon: SiShell, color: "text-green-600" },

  // Build & Dependencies
  "package.json": { icon: SiNodedotjs, color: "text-green-600" },
  "package-lock.json": { icon: SiNodedotjs, color: "text-green-600" },
  "yarn.lock": { icon: SiYarn, color: "text-blue-400" },
  gradle: { icon: SiGradle, color: "text-green-500" },

  // Development Tools
  gitignore: { icon: SiGit, color: "text-gray-500" },
  dockerfile: { icon: SiDocker, color: "text-blue-400" },
  dockerignore: { icon: SiDocker, color: "text-blue-400" },

  // Database
  sql: { icon: SiPostgresql, color: "text-blue-400" },
  prisma: { icon: SiPrisma, color: "text-teal-500" },

  // Framework Config Files
  "next.config.js": {
    icon: SiNextdotjs,
    color: "text-gray-900 dark:text-white",
  },
  "nuxt.config.js": { icon: SiNuxtdotjs, color: "text-green-500" },
  "electron.config.js": { icon: SiElectron, color: "text-blue-400" },
  "tailwind.config.js": { icon: SiTailwindcss, color: "text-teal-500" },
  "redux.js": { icon: SiRedux, color: "text-purple-500" },
  "graphql.js": { icon: SiGraphql, color: "text-pink-600" },
};

export const directoryIcons: DirectoryIconMapping = {
  // Common development directories
  src: {
    icon: VscSourceControl,
    color: "text-yellow-600 dark:text-yellow-500",
  },
  app: { icon: VscProject, color: "text-yellow-600 dark:text-yellow-500" },
  components: {
    icon: VscSymbolNamespace,
    color: "text-green-600 dark:text-green-500",
  },
  pages: { icon: VscSymbolNamespace, color: "text-purple-500" },
  assets: { icon: VscFileMedia, color: "text-yellow-600" },
  public: { icon: VscFileMedia, color: "text-green-600" },
  lib: { icon: VscFolderLibrary, color: "text-blue-600" },
  utils: { icon: VscTools, color: "text-gray-600" },
  helpers: { icon: VscTools, color: "text-gray-600" },
  tests: { icon: VscBeaker, color: "text-orange-500" },
  __tests__: { icon: VscBeaker, color: "text-orange-500" },
  config: { icon: VscSettingsGear, color: "text-gray-500" },
  types: { icon: SiTypescript, color: "text-blue-600" },
  interfaces: { icon: SiTypescript, color: "text-blue-600" },
  models: { icon: VscJson, color: "text-purple-500" },
  api: { icon: VscSymbolNamespace, color: "text-green-600" },
  routes: { icon: VscSymbolNamespace, color: "text-blue-500" },
  middleware: { icon: VscSymbolNamespace, color: "text-orange-500" },
  hooks: { icon: DiReact, color: "text-blue-400" },
  contexts: { icon: DiReact, color: "text-blue-400" },
  styles: { icon: DiCss3, color: "text-blue-500" },
  images: { icon: VscFileMedia, color: "text-purple-500" },
  fonts: { icon: VscFileMedia, color: "text-yellow-500" },
  docs: { icon: SiMarkdown, color: "text-blue-500" },
  documentation: { icon: SiMarkdown, color: "text-blue-500" },
  node_modules: { icon: SiNodedotjs, color: "text-green-600" },
  dist: { icon: VscPackage, color: "text-yellow-500" },
  build: { icon: VscPackage, color: "text-yellow-500" },
  ".git": { icon: VscGithub, color: "text-gray-500" },
  ".github": { icon: VscGithub, color: "text-gray-500" },
  ".idea": { icon: VscSymbolNamespace, color: "text-gray-500" },
};

export const getFileIcon = (
  fileName: string,
  isDirectory: boolean = false
): JSX.Element => {
  if (isDirectory) {
    const dirConfig = directoryIcons[fileName] || {
      icon: VscFolder,
      color: "text-blue-600 dark:text-blue-500",
    };
    const { icon: Icon, color } = dirConfig;
    return <Icon size={16} className={color} />;
  }

  // Check for exact file name matches first
  if (fileIcons[fileName]) {
    const { icon: Icon, color } = fileIcons[fileName];
    return <Icon size={16} className={color} />;
  }

  // Check file extension
  const extension = fileName.split(".").pop()?.toLowerCase() ?? "";
  const iconConfig = fileIcons[extension] || {
    icon: VscFile,
    color: "text-gray-600 dark:text-gray-500",
  };
  const { icon: Icon, color } = iconConfig;

  return <Icon size={16} className={color} />;
};
